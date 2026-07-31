from typing import List, Dict, Optional, Any
from ai_models.model_registry.models import ModelSpecs

class ModelRegistry:
    def __init__(self):
        self._models: Dict[str, ModelSpecs] = {}
        self._register_default_models()

    def register_model(self, specs: ModelSpecs):
        """Registers or updates a model specification in the registry."""
        self._models[specs.id] = specs

    def _register_default_models(self):
        # Register GGUF local models first
        self.register_model(ModelSpecs(
            id="qwen-model.gguf",
            name="Qwen 2.5 3B (GGUF)",
            family="Qwen",
            engine="gguf",
            size_gb=2.0,
            parameters="3B",
            max_context=4096,
            streaming=True,
            ram_estimated_gb=4.0,
            precision="q4_K_M"
        ))
        self.register_model(ModelSpecs(
            id="coder-model.gguf",
            name="Qwen Coder 1.5B (GGUF)",
            family="Qwen",
            engine="gguf",
            size_gb=1.2,
            parameters="1.5B",
            max_context=4096,
            streaming=True,
            ram_estimated_gb=3.0,
            precision="q4_K_M"
        ))
        self.register_model(ModelSpecs(
            id="reasoning-model.gguf",
            name="DeepSeek R1 Distill 1.5B (GGUF)",
            family="DeepSeek",
            engine="gguf",
            size_gb=1.2,
            parameters="1.5B",
            max_context=4096,
            streaming=True,
            ram_estimated_gb=3.0,
            precision="q4_K_M"
        ))

        # Register standard offline Ollama models
        self.register_model(ModelSpecs(
            id="qwen2.5:3b",
            name="Qwen 2.5 3B",
            family="Qwen",
            engine="ollama",
            size_gb=1.9,
            parameters="3B",
            max_context=4096,
            streaming=True,
            tools=True,
            embeddings=False,
            ram_estimated_gb=4.0,
            precision="q4_K_M"
        ))
        self.register_model(ModelSpecs(
            id="llama3:8b",
            name="Llama 3 8B",
            family="Llama",
            engine="ollama",
            size_gb=4.7,
            parameters="8B",
            max_context=8192,
            streaming=True,
            tools=True,
            embeddings=False,
            ram_estimated_gb=8.0,
            precision="q4_K_M"
        ))
        self.register_model(ModelSpecs(
            id="mistral:7b",
            name="Mistral 7B",
            family="Mistral",
            engine="ollama",
            size_gb=4.1,
            parameters="7B",
            max_context=8192,
            streaming=True,
            tools=False,
            embeddings=False,
            ram_estimated_gb=8.0,
            precision="q4_K_M"
        ))
        self.register_model(ModelSpecs(
            id="phi3:3.8b",
            name="Phi 3 3.8B",
            family="Phi",
            engine="ollama",
            size_gb=2.2,
            parameters="3.8B",
            max_context=4096,
            streaming=True,
            tools=False,
            embeddings=False,
            ram_estimated_gb=4.0,
            precision="q4_K_M"
        ))
        self.register_model(ModelSpecs(
            id="gemma:2b",
            name="Gemma 2B",
            family="Gemma",
            engine="ollama",
            size_gb=1.4,
            parameters="2B",
            max_context=2048,
            streaming=True,
            tools=False,
            embeddings=False,
            ram_estimated_gb=3.0,
            precision="q4_K_M"
        ))
        self.register_model(ModelSpecs(
            id="deepseek-coder:1.5b",
            name="DeepSeek Coder 1.5B",
            family="DeepSeek",
            engine="ollama",
            size_gb=0.9,
            parameters="1.5B",
            max_context=4096,
            streaming=True,
            tools=False,
            embeddings=False,
            ram_estimated_gb=3.0,
            precision="q4_K_M"
        ))

        # GGUF Engine Legacy
        self.register_model(ModelSpecs(
            id="llama3-8b-q4_k_m.gguf",
            name="Llama 3 8B (GGUF)",
            family="Llama",
            engine="gguf",
            size_gb=4.7,
            parameters="8B",
            max_context=8192,
            streaming=True,
            ram_estimated_gb=8.0,
            precision="q4_K_M"
        ))
        # Transformers Engine
        self.register_model(ModelSpecs(
            id="qwen2.5-coder-hf",
            name="Qwen 2.5 Coder HF",
            family="Qwen",
            engine="transformers",
            size_gb=6.0,
            parameters="3B",
            max_context=4096,
            streaming=True,
            ram_estimated_gb=8.0
        ))
        # Future Cloud
        self.register_model(ModelSpecs(
            id="gpt-4o",
            name="GPT-4o",
            family="GPT",
            engine="cloud",
            size_gb=0.0,
            parameters="unknown",
            max_context=128000,
            streaming=True
        ))

    def get_model(self, model_id: str) -> Optional[ModelSpecs]:
        """Gets a model specification by ID."""
        return self._models.get(model_id)

    def list_models(self) -> List[ModelSpecs]:
        """Lists all registered model specifications."""
        return list(self._models.values())

    def list_by_engine(self, engine: str) -> List[ModelSpecs]:
        """Lists all models belonging to a specific engine."""
        return [m for m in self._models.values() if m.engine == engine]

    def get_capabilities(self, model_id: str) -> Dict[str, Any]:
        """Helper to retrieve all capability flags of a model."""
        m = self.get_model(model_id)
        if not m:
            return {}
        return {
            "streaming": m.streaming,
            "vision": m.vision,
            "audio": m.audio,
            "tools": m.tools,
            "embeddings": m.embeddings,
            "max_context": m.max_context,
            "gpu_required": m.gpu_required,
            "ram_estimated_gb": m.ram_estimated_gb
        }

global_model_registry = ModelRegistry()
