from typing import Dict, List, Set
from contracts.models import Capability
from ai_models.model_registry.service import global_model_registry

class FeatureCapabilityRegistry:
    def __init__(self):
        pass

    def get_capabilities(self, model_id: str) -> Set[Capability]:
        """Discovers and returns all capabilities supported by a model."""
        specs = global_model_registry.get_model(model_id)
        caps = set()
        if not specs:
            return caps

        # Map specs attributes to Capability enums
        caps.add(Capability.TEXT_GENERATION) # All conversational models do text generation
        if specs.streaming:
            caps.add(Capability.STREAMING)
        if specs.tools:
            caps.add(Capability.TOOL_CALLING)
        if specs.vision:
            caps.add(Capability.VISION)
        if specs.audio:
            caps.add(Capability.AUDIO_INPUT)
        if specs.embeddings:
            caps.add(Capability.EMBEDDING)
        return caps

global_capability_registry = FeatureCapabilityRegistry()
