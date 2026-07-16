from abc import ABC, abstractmethod

class BaseAIModel(ABC):
    def __init__(self, model_name):
        self.model_name = model_name
        self.loaded = False
    @abstractmethod
    def load(self) -> bool: pass
    @abstractmethod
    def unload(self) -> bool: pass
    @abstractmethod
    def predict(self, inputs): pass
    @abstractmethod
    def status(self): pass
    @abstractmethod
    def get_information(self): pass
