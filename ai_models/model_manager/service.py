import os
import yaml
from typing import List, Dict, Any, Optional, Iterator
from ai_models.model_registry.service import global_model_registry
from ai_models.llm.engines import LLMFactory
from ai_models.llm.models import LLMResponse

class ModelManager:
    def __init__(self):
        self.config = self._load_config()
        self.active_engine_name = self.config.get("active_engine", "gguf") # Default to GGUF local core as requested!
        self.active_model_name = self.config.get("active_model", "qwen-model.gguf")

        # Instantiate active LLM engine
        self._engine = LLMFactory.create_engine(self.active_engine_name, self.active_model_name, self.config)
        self._engine.load_model()

    def _load_config(self) -> Dict[str, Any]:
        config_path = "config/llm.yaml"
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception:
                pass
        return {}

    def detect_hardware_compatibility(self, model_id: str) -> Dict[str, Any]:
        """Checks if the system has enough RAM/VRAM to run a registered model."""
        specs = global_model_registry.get_model(model_id)
        if not specs:
            return {"compatible": False, "reason": "Modèle inconnu"}

        from core.system.service import global_resource_monitor
        metrics = global_resource_monitor.get_metrics()
        ram_avail = metrics.get("ram_available_gb", 8.0)

        compatible = ram_avail >= specs.ram_estimated_gb
        return {
            "compatible": compatible,
            "ram_required_gb": specs.ram_estimated_gb,
            "ram_available_gb": round(ram_avail, 2),
            "reason": "Ressources système suffisantes" if compatible else "RAM insuffisante"
        }

    def load_model(self, model_id: str) -> bool:
        """Loads a model from the registry by ID."""
        specs = global_model_registry.get_model(model_id)
        if not specs:
            return False

        self._engine.unload_model()
        self.active_engine_name = specs.engine
        self.active_model_name = specs.id
        self._engine = LLMFactory.create_engine(specs.engine, specs.id, self.config)
        return self._engine.load_model()

    def change_model(self, engine_type: str, model_name: str) -> bool:
        """Centralized method to dynamically switch the LLM backend or model."""
        self._engine.unload_model()
        self.active_engine_name = engine_type
        self.active_model_name = model_name
        self._engine = LLMFactory.create_engine(engine_type, model_name, self.config)
        return self._engine.load_model()

    def select_best_model_for_intent(self, intent: str) -> str:
        """Selects the most suitable model from the active engine according to capabilities and intent."""
        if self.active_engine_name == "gguf":
            # Map intents to GGUF model filenames in our multi-model folders
            intent_lower = str(intent).lower()
            if any(k in intent_lower for k in ["code", "développement", "developpement", "generation", "modification", "programmation", "software"]):
                return "coder-model.gguf"
            elif any(k in intent_lower for k in ["complex", "requêtes complexes", "planning", "raisonnement", "reasoning", "sécurité", "security"]):
                return "reasoning-model.gguf"
            else:
                return "qwen-model.gguf"

        # If other engine (e.g. Ollama)
        available = global_model_registry.list_by_engine(self.active_engine_name)
        if not available:
            return self.active_model_name

        intent_lower = str(intent).lower()
        if any(k in intent_lower for k in ["code", "développement", "developpement", "generation", "modification", "programmation"]):
            code_mods = [m.id for m in available if "coder" in m.id or "deepseek" in m.id]
            if code_mods:
                return code_mods[0]

        if any(k in intent_lower for k in ["complex", "planning", "reasoning"]):
            reason_mods = [m.id for m in available if "llama3" in m.id or "mistral" in m.id or "8b" in m.id]
            if reason_mods:
                return reason_mods[0]

        return self.active_model_name

    def generate(self, prompt: str, system: str = "", intent: str = "Inconnu") -> LLMResponse:
        """Sends inference task to the currently loaded model engine."""
        target_model = self.select_best_model_for_intent(intent)

        # Temporary model switch if different
        original_model = self.active_model_name
        if target_model != original_model:
            self.load_model(target_model)

        response = self._engine.generate(prompt, system)

        # Restore original
        if target_model != original_model:
            self.load_model(original_model)

        # Set engine and other rich fields on response
        response.metadata["engine"] = self.active_engine_name
        return response

    def generate_stream(self, prompt: str, system: str = "", intent: str = "Inconnu") -> Iterator[LLMResponse]:
        """Provides streaming interface to generate responses progressively."""
        target_model = self.select_best_model_for_intent(intent)
        original_model = self.active_model_name
        if target_model != original_model:
            self.load_model(target_model)

        for chunk in self._engine.generate_stream(prompt, system):
            chunk.metadata["engine"] = self.active_engine_name
            yield chunk

        if target_model != original_model:
            self.load_model(original_model)

    def list_available_models(self) -> List[str]:
        """Lists IDs of registered models for active engine."""
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
