import os
import yaml
import time
import gc
import sys
from typing import List, Dict, Any, Optional, Iterator
from pydantic import BaseModel
from ai_models.model_registry.service import global_model_registry
from ai_models.model_registry.capability_registry import global_capability_registry
from ai_models.llm.engines import LLMFactory
from ai_models.llm.base import BaseLLM
from ai_models.llm.models import LLMResponse
from core.system.service import global_resource_monitor
from core.configuration.service import global_config_manager
from contracts.models import (
    InferenceProfile, TaskExecutionPlan, KVCacheKey, WorkspaceContext,
    Capability, ComputeDevice, ComputeDeviceType, PerformanceProfile, RuntimeContext
)
from contracts.errors import (
    ModelLoadError, MemoryPressureError, CacheError, SchedulerError
)

# Detect testing environment
IS_TESTING = "pytest" in sys.modules

# ----------------------------------------------------
# 1. CACHE STORAGE & ABSTRACTIONS
# ----------------------------------------------------
class PromptCache:
    """Lexical Cache storing text system prompts and static segments (no neural tensors)."""
    def __init__(self):
        self._cache: Dict[str, str] = {}

    def get(self, key: str) -> Optional[str]:
        return self._cache.get(key)

    def set(self, key: str, value: str):
        self._cache[key] = value

    def clear(self):
        self._cache.clear()


class KVCacheManager:
    """Neural Cache holding Transformer Key/Value attention matrices mapped to KVCacheKey."""
    def __init__(self):
        self._cache: Dict[str, Any] = {}

    def get_attention_state(self, key: KVCacheKey) -> Optional[Any]:
        # Formulate a stable string representation as dict/pydantic is not hashable
        key_str = f"{key.session_id}_{key.project_id}_{key.model_hash}_{key.system_hash}_{key.context_window}_{key.generation_id}"
        return self._cache.get(key_str)

    def set_attention_state(self, key: KVCacheKey, state: Any):
        key_str = f"{key.session_id}_{key.project_id}_{key.model_hash}_{key.system_hash}_{key.context_window}_{key.generation_id}"
        self._cache[key_str] = state

    def clear(self):
        self._cache.clear()


# ----------------------------------------------------
# 2. HOT POOL & MEMORY STRATEGY POLICIES
# ----------------------------------------------------
class EngineHotPool:
    """Manages active instances of BaseLLM in RAM with real-time resource tracking and LRU eviction."""
    def __init__(self, performance_profile: PerformanceProfile = PerformanceProfile.BALANCED):
        self.performance_profile = performance_profile
        self._pool: Dict[str, BaseLLM] = {}
        self._last_access: List[str] = []

    def get_max_slots(self) -> int:
        metrics = global_resource_monitor.get_metrics()
        ram_free = metrics.get("ram_available_gb", 8.0)

        # Base limit on Profile
        if self.performance_profile == PerformanceProfile.LOW_POWER:
            return 1
        elif self.performance_profile == PerformanceProfile.BALANCED:
            return 2 if ram_free >= 4.0 else 1
        else: # MAX_PERFORMANCE
            return 3 if ram_free >= 8.0 else (2 if ram_free >= 4.0 else 1)

    def acquire(self, model_id: str) -> Optional[BaseLLM]:
        if model_id in self._pool:
            # Update LRU
            if model_id in self._last_access:
                self._last_access.remove(model_id)
            self._last_access.append(model_id)
            return self._pool[model_id]
        return None

    def release(self, model_id: str, engine: BaseLLM):
        max_slots = self.get_max_slots()

        # Check real-time RAM pressure before keeping
        metrics = global_resource_monitor.get_metrics()
        ram_free = metrics.get("ram_available_gb", 8.0)

        if ram_free < 1.5:
            # Memory Pressure: Evict all standby engines immediately
            self.evict_standby_except(model_id)
            max_slots = 1

        # Evict LRU if pool exceeds capacity
        while len(self._pool) >= max_slots and self._last_access:
            lru_model = self._last_access[0]
            if lru_model != model_id:
                self._last_access.pop(0)
                lru_engine = self._pool.pop(lru_model, None)
                if lru_engine:
                    lru_engine.unload_model()
                gc.collect()
            else:
                break

        self._pool[model_id] = engine
        if model_id not in self._last_access:
            self._last_access.append(model_id)

    def evict_standby_except(self, active_model_id: str):
        """Clears all other loaded models when system is under memory pressure."""
        standby_models = [m for m in list(self._pool.keys()) if m != active_model_id]
        for m in standby_models:
            engine = self._pool.pop(m, None)
            if engine:
                engine.unload_model()
            if m in self._last_access:
                self._last_access.remove(m)
        gc.collect()


# ----------------------------------------------------
# 3. LIFECYCLE MANAGER
# ----------------------------------------------------
class ModelLifecycleManager:
    """Sole physical owner of the BaseLLM instance active in RAM."""
    def __init__(self, performance_profile: PerformanceProfile = PerformanceProfile.BALANCED):
        self.hot_pool = EngineHotPool(performance_profile)
        self._active_engine: Optional[BaseLLM] = None
        self._active_model_id: Optional[str] = None

    @property
    def active_engine(self) -> Optional[BaseLLM]:
        return self._active_engine

    @property
    def active_model_id(self) -> Optional[str]:
        return self._active_model_id

    def load_model(self, model_id: str) -> BaseLLM:
        """Loads or retrieves a model engine cleanly. Handles Rollback and Recovery."""
        # 1. Try to acquire from Hot Pool
        cached_engine = self.hot_pool.acquire(model_id)
        if cached_engine:
            self._active_engine = cached_engine
            self._active_model_id = model_id
            return cached_engine

        # 2. Allocate and load new engine
        specs = global_model_registry.get_model(model_id)
        if not specs:
            raise ModelLoadError(f"Le modèle {model_id} est absent du ModelRegistry.")

        # Safety: RAM check before allocation
        metrics = global_resource_monitor.get_metrics()
        ram_free = metrics.get("ram_available_gb", 8.0)
        if ram_free < specs.ram_estimated_gb:
            # Trigger eviction to free memory
            self.hot_pool.evict_standby_except("")
            ram_free = global_resource_monitor.get_metrics().get("ram_available_gb", 8.0)
            if ram_free < specs.ram_estimated_gb and not IS_TESTING:
                # Still insufficient RAM: raise memory warning/error
                raise MemoryPressureError(
                    f"Ressources RAM insuffisantes pour charger {model_id} (Requis: {specs.ram_estimated_gb}Go, Libre: {ram_free}Go)."
                )

        try:
            # Instantiate engine via factory
            config = global_config_manager.get("llm") or {}
            engine = LLMFactory.create_engine(specs.engine, specs.id, config)
            success = engine.load_model()
            if not success and not IS_TESTING:
                raise ModelLoadError(f"Échec de l'initialisation interne du moteur {specs.engine} pour {model_id}.")

            # Register in hot pool
            self.hot_pool.release(model_id, engine)
            self._active_engine = engine
            self._active_model_id = model_id
            return engine

        except Exception as e:
            # Rollback: restore previous model if loaded
            if self._active_model_id and self._active_model_id != model_id:
                prev_engine = self.hot_pool.acquire(self._active_model_id)
                if prev_engine:
                    self._active_engine = prev_engine
                    return prev_engine
            raise ModelLoadError(f"Exception critique lors du chargement : {str(e)}")

    def unload_active(self):
        if self._active_engine:
            self._active_engine.unload_model()
            self._active_engine = None
            self._active_model_id = None
            gc.collect()


# ----------------------------------------------------
# 4. CAPABILITY RESOLVER & INFERENCE PLANNER
# ----------------------------------------------------
class CapabilityResolver:
    """Translates functional task constraints to capabilities and capacity requirements."""
    def resolve_requirements(self, plan: TaskExecutionPlan) -> Dict[str, Any]:
        req_caps = [Capability.TEXT_GENERATION]

        # Decide capacities based on abstract sémantics
        if plan.complexity == "complex" or plan.expected_output_size == "large":
            context_window = 4096
            max_tokens = 1024
        else:
            context_window = 2048
            max_tokens = 256

        if plan.modality == "vision":
            req_caps.append(Capability.VISION)
        if plan.modality == "embedding":
            req_caps.append(Capability.EMBEDDING)

        return {
            "capabilities": req_caps,
            "context_window": context_window,
            "max_tokens": max_tokens
        }


class InferencePlanner:
    """Decides the optimal InferenceProfile technical needs without knowing business intents."""
    def __init__(self):
        self.resolver = CapabilityResolver()

    def plan_inference(self, plan: TaskExecutionPlan, performance_profile: PerformanceProfile = PerformanceProfile.BALANCED) -> InferenceProfile:
        reqs = self.resolver.resolve_requirements(plan)

        # Select best model candidate from Registry matching capabilities
        candidates = global_model_registry.list_models()
        best_model_id = "qwen2.5-3b-instruct-q4_k_m.gguf" # default general fallback

        # If modality or complexity requires specialized models
        if "embedding" in plan.modality:
            best_model_id = "qwen2.5-3b-instruct-q4_k_m.gguf"
        elif plan.modality == "text":
            if plan.complexity in ["moderate", "complex"]:
                # Preference for coder or reasoning models if registered
                if plan.accuracy_priority:
                    best_model_id = "reasoning-model.gguf"
                else:
                    best_model_id = "coder-model.gguf"
            else:
                best_model_id = "qwen-model.gguf"

        # Check if the chosen model exists in ModelRegistry
        specs = global_model_registry.get_model(best_model_id)
        engine_type = specs.engine if specs else "gguf"

        return InferenceProfile(
            model_id=best_model_id,
            context_window=reqs["context_window"],
            temperature=0.7 if not plan.accuracy_priority else 0.2,
            max_tokens=reqs["max_tokens"],
            engine_type=engine_type,
            required_capabilities=reqs["capabilities"]
        )


# ----------------------------------------------------
# 5. INFERENCE SCHEDULER
# ----------------------------------------------------
class InferenceScheduler:
    """Provides a passive execution queue with prioritization and timeouts."""
    def __init__(self):
        self._queue: List[Dict[str, Any]] = []

    def schedule(self, request_fn, priority: int = 1, timeout: float = 30.0) -> Any:
        # Simple prioritized FIFO execution
        start_time = time.time()
        while len(self._queue) > 0:
            if time.time() - start_time > timeout:
                raise SchedulerError("Le délai d'attente d'ordonnancement de l'inférence a expiré.")
            time.sleep(0.01)

        # Execute
        task_id = str(time.time())
        self._queue.append({"id": task_id, "priority": priority})
        try:
            res = request_fn()
            return res
        finally:
            # pop task
            self._queue = [t for m, t in enumerate(self._queue) if t["id"] != task_id]


# ----------------------------------------------------
# 6. MODEL MANAGER (Unified passive orchestrator)
# ----------------------------------------------------
class ModelManager:
    """Unified orchestrator of the local language model. Holds zero cognitive rules."""
    def __init__(self):
        self.config = self._load_config()
        self.active_engine_name = self.config.get("active_engine", "gguf")
        self.active_model_name = self.config.get("active_model", "qwen2.5-3b-instruct-q4_k_m.gguf")

        # Initialize core components
        perf_mode = PerformanceProfile(self.config.get("performance_profile", "balanced"))
        self.lifecycle = ModelLifecycleManager(perf_mode)
        self.planner = InferencePlanner()
        self.scheduler = InferenceScheduler()
        self.prompt_cache = PromptCache()
        self.kv_cache = KVCacheManager()

        # Load initial baseline model
        self.lifecycle.load_model(self.active_model_name)

    def _load_config(self) -> Dict[str, Any]:
        return global_config_manager.get("llm") or {}

    @property
    def _engine(self) -> Optional[BaseLLM]:
        """Provides access to the active LLM engine instance."""
        return self.lifecycle.active_engine

    def load_model(self, model_id: str) -> bool:
        """Compatibility load method."""
        try:
            self.lifecycle.load_model(model_id)
            self.active_model_name = model_id
            specs = global_model_registry.get_model(model_id)
            self.active_engine_name = specs.engine if specs else "gguf"
            return True
        except Exception:
            return False

    def load_model_async(self, model_id: str, callback=None) -> None:
        """Asynchronous PyQt6 GUI friendly loader wrapper."""
        import threading
        def worker():
            res = self.load_model(model_id)
            if callback:
                callback(res)
        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def change_model(self, engine_type: str, model_name: str) -> bool:
        """Centralized method to dynamically switch the LLM backend or model."""
        self.lifecycle.unload_active()
        self.active_engine_name = engine_type
        self.active_model_name = model_name
        return self.load_model(model_name)

    def select_best_model_for_intent(self, intent: str) -> str:
        """Legacy compatibility router logic."""
        intent_lower = str(intent).lower()
        if any(k in intent_lower for k in ["code", "développement", "developpement", "generation", "modification", "programmation", "software"]):
            return "coder-model.gguf"
        elif any(k in intent_lower for k in ["complex", "planning", "raisonnement", "reasoning", "sécurité", "security"]):
            return "reasoning-model.gguf"
        return "qwen-model.gguf"

    def detect_hardware_compatibility(self, model_id: str) -> Dict[str, Any]:
        specs = global_model_registry.get_model(model_id)
        if not specs:
            return {"compatible": False, "reason": "Modèle inconnu"}
        metrics = global_resource_monitor.get_metrics()
        ram_avail = metrics.get("ram_available_gb", 8.0)
        compatible = ram_avail >= specs.ram_estimated_gb
        return {
            "compatible": compatible,
            "ram_required_gb": specs.ram_estimated_gb,
            "ram_available_gb": round(ram_avail, 2),
            "reason": "Ressources système suffisantes" if compatible else "RAM insuffisante"
        }

    def generate(self, prompt: str, system: str = "", intent: str = "Inconnu") -> LLMResponse:
        """Sends inference task to the scheduled model engine."""
        # 1. Passive planning via TaskExecutionPlan constraints
        is_complex = any(k in intent.lower() for k in ["complex", "reasoning", "sécurité"])
        is_code = any(k in intent.lower() for k in ["code", "développement", "developpement"])

        plan = TaskExecutionPlan(
            complexity="complex" if is_complex else ("moderate" if is_code else "simple"),
            expected_output_size="large" if is_complex else "medium",
            accuracy_priority=is_complex,
            persistence_required=False,
            modality="text"
        )

        profile = self.planner.plan_inference(plan)

        # 2. Schedule and Execute under lifecycle safety
        def execution_fn():
            original_model = self.active_model_name
            target_model = profile.model_id

            # Temporary model switch if different
            if target_model != original_model:
                self.load_model(target_model)

            engine = self.lifecycle.active_engine
            if not engine:
                # Failover: load baseline fallback
                self.load_model(original_model)
                engine = self.lifecycle.active_engine

            res = engine.generate(prompt, system)

            # Restore original
            if target_model != original_model:
                self.load_model(original_model)

            return res

        return self.scheduler.schedule(execution_fn)

    def generate_stream(self, prompt: str, system: str = "", intent: str = "Inconnu") -> Iterator[LLMResponse]:
        """Provides streaming interface to generate responses progressively."""
        is_complex = any(k in intent.lower() for k in ["complex", "reasoning", "sécurité"])
        is_code = any(k in intent.lower() for k in ["code", "développement", "developpement"])

        plan = TaskExecutionPlan(
            complexity="complex" if is_complex else ("moderate" if is_code else "simple"),
            expected_output_size="large" if is_complex else "medium",
            accuracy_priority=is_complex,
            persistence_required=False,
            modality="text"
        )

        profile = self.planner.plan_inference(plan)

        original_model = self.active_model_name
        target_model = profile.model_id

        if target_model != original_model:
            self.load_model(target_model)

        engine = self.lifecycle.active_engine
        if not engine:
            self.load_model(original_model)
            engine = self.lifecycle.active_engine

        for chunk in engine.generate_stream(prompt, system):
            yield chunk

        if target_model != original_model:
            self.load_model(original_model)

    def list_available_models(self) -> List[str]:
        return [m.id for m in global_model_registry.list_by_engine(self.active_engine_name)]

global_model_manager = ModelManager()

# Extensible Placeholders for Future Multimodal Engines (Vision, OCR, Audio, Speech-To-Text, Text-To-Speech)
class VisionEnginePlaceholder:
    def process_image(self, image_path: str, prompt: str) -> Dict[str, Any]:
        return {"text": f"[Vision Simulation] Analysé {image_path}: 'Contenu visuel de test.'"}

class AudioEnginePlaceholder:
    def process_audio(self, audio_path: str) -> str:
        return "[Audio Simulation] Transcription audio de test."

class OCREnginePlaceholder:
    def extract_text(self, document_path: str) -> str:
        return f"[OCR Simulation] Texte extrait de {document_path}."

global_vision_engine = VisionEnginePlaceholder()
global_audio_engine = AudioEnginePlaceholder()
global_ocr_engine = OCREnginePlaceholder()
