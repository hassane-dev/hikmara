from abc import ABC, abstractmethod
from typing import List

class BaseEmbedding(ABC):
    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generates embedding vector for a single text."""
        pass

    @abstractmethod
    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Generates embedding vectors for a list of documents."""
        pass
