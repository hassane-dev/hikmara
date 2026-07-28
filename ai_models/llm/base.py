from abc import ABC, abstractmethod
from typing import List, Dict, Any, Iterator
from ai_models.llm.models import LLMResponse

class BaseLLM(ABC):
    def __init__(self, model_name: str, config: Dict[str, Any] = None):
        self.model_name = model_name
        self.config = config or {}
        self.loaded = False

    @abstractmethod
    def load_model(self) -> bool:
        pass

    @abstractmethod
    def unload_model(self) -> bool:
        pass

    @abstractmethod
    def generate(self, prompt: str, system: str = "") -> LLMResponse:
        pass

    @abstractmethod
    def generate_stream(self, prompt: str, system: str = "") -> Iterator[LLMResponse]:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        pass

    @abstractmethod
    def switch_model(self, model_name: str) -> bool:
        pass

    @abstractmethod
    def supports_streaming(self) -> bool:
        pass

    @abstractmethod
    def supports_tools(self) -> bool:
        pass

    # Compatibility methods to prevent breakage on other legacy references
    def load(self) -> bool:
        return self.load_model()

    def unload(self) -> bool:
        return self.unload_model()

    def predict(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        prompt = inputs.get("prompt", "")
        system = inputs.get("system_prompt", "")
        response_obj = self.generate(prompt, system)
        return {"response": response_obj.text, "model": self.model_name}
