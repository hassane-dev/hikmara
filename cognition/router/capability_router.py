from typing import Dict, Any
from ai_models.model_registry.service import global_model_registry

class CapabilityRouter:
    def __init__(self):
        pass

    def check_capabilities(self, model_id: str) -> Dict[str, Any]:
        """Looks up the capabilities of a model from the registry."""
        specs = global_model_registry.get_model(model_id)
        if not specs:
            return {
                "streaming": False,
                "vision": False,
                "audio": False,
                "tools": False,
                "embeddings": False,
                "gpu_required": False,
                "ram_estimated_gb": 4.0,
                "max_context": 2048
            }
        return {
            "streaming": specs.streaming,
            "vision": specs.vision,
            "audio": specs.audio,
            "tools": specs.tools,
            "embeddings": specs.embeddings,
            "gpu_required": specs.gpu_required,
            "ram_estimated_gb": specs.ram_estimated_gb,
            "max_context": specs.max_context
        }

global_capability_router = CapabilityRouter()
