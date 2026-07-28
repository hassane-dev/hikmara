import os
import yaml
from typing import List, Dict, Any
from ai_models.llm.engines import LLMFactory
from ai_models.llm.models import LLMResponse

class ModelManager:
    def __init__(self):
        # Load local LLM configuration
        config_path = "config/llm.yaml"
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    self.config = yaml.safe_load(f) or {}
            except Exception:
                self.config = {}
        else:
            self.config = {}

        self.active_engine_name = self.config.get("active_engine", "ollama")
        self.active_model_name = self.config.get("active_model", "qwen2.5:3b")

        # Instantiate active LLM engine
        self._engine = LLMFactory.create_engine(self.active_engine_name, self.active_model_name, self.config)
        self._engine.load_model()

    def detect_hardware_compatibility(self, size_gb: float) -> bool:
        # Simple simulated RAM capacity check
        from core.system.service import global_resource_monitor
        m = global_resource_monitor.get_metrics()
        return m.get("ram_available_gb", 8.0) > size_gb

    def load_model(self, model_id: str, inst: Any) -> bool:
        self._engine = inst
        self.active_model_name = model_id
        return self._engine.load_model()

    def change_model(self, engine_type: str, model_name: str) -> bool:
        """Centralized method to dynamically switch the LLM backend or model."""
        self._engine.unload_model()
        self.active_engine_name = engine_type
        self.active_model_name = model_name
        self._engine = LLMFactory.create_engine(engine_type, model_name, self.config)
        return self._engine.load_model()

    def select_best_model_for_intent(self, intent: str) -> str:
        """Heuristics to assign the most optimal local model based on intent (Multi-LLM)."""
        available = self._engine.list_models()
        if intent in ["Génération de code", "Développement logiciel"]:
            # Prefer code models if available
            code_candidates = [m for m in available if "coder" in m or "deepseek" in m]
            return code_candidates[0] if code_candidates else self.active_model_name
        elif intent in ["Salutations", "Conversation générale"]:
            # Prefer small models if available
            small_candidates = [m for m in available if "gemma" in m or "phi" in m or "2b" in m]
            return small_candidates[0] if small_candidates else self.active_model_name
        return self.active_model_name

    def generate(self, prompt: str, system: str = "", intent: str = "Inconnu") -> LLMResponse:
        """Centralized generator dispatching queries to the best suited active engine model."""
        target_model = self.select_best_model_for_intent(intent)

        # Temporarily switch if needed (simulated model choice)
        original_model = self.active_model_name
        if target_model != original_model:
            self._engine.switch_model(target_model)

        response = self._engine.generate(prompt, system)

        # Restore original model
        if target_model != original_model:
            self._engine.switch_model(original_model)

        return response

    def list_available_models(self) -> List[str]:
        return self._engine.list_models()

global_model_manager = ModelManager()
