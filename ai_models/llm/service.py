from ai_models.base_model import BaseAIModel
from ai_models.llm.engines import LLMFactory

class LLMEngine(BaseAIModel):
    """
    Decoupled compatibility wrapper around LLMFactory engines.
    Exposes BaseAIModel signature to remain compatible with legacy references.
    """
    def __init__(self, model_name="qwen2.5:3b"):
        super().__init__(model_name)
        self.engine_impl = LLMFactory.create_engine("ollama", model_name)

    def load(self):
        self.loaded = self.engine_impl.load_model()
        return self.loaded

    def unload(self):
        self.loaded = not self.engine_impl.unload_model()
        return not self.loaded

    def predict(self, inputs):
        """Standard generic offline generation predict signature."""
        prompt = inputs.get("prompt", "")
        system = inputs.get("system_prompt", "")
        response_obj = self.engine_impl.generate(prompt, system)
        return {"response": response_obj.text, "model": self.model_name}

    def status(self):
        return {"loaded": self.loaded}

    def get_information(self):
        return {"type": "LLM", "model": self.model_name}
