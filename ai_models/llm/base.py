from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseLLM(ABC):
    def __init__(self, model_name: str, config: Dict[str, Any] = None):
        self.model_name = model_name
        self.config = config or {}
        self.loaded = False

    @abstractmethod
    def load(self) -> bool:
        pass

    @abstractmethod
    def unload(self) -> bool:
        pass

    @abstractmethod
    def predict(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        pass
