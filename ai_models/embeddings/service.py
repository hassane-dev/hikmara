import numpy as np
from typing import List
from ai_models.embeddings.base import BaseEmbedding

class SentenceTransformersEmbedding(BaseEmbedding):
    def embed_text(self, text: str) -> List[float]:
        # Offline deterministic vector simulation using word length hashing
        # This keeps representation stable and offline-first without PyTorch overhead during quick simulation tests
        state = np.random.RandomState(sum(ord(c) for c in text) % 2**32)
        return state.normal(0.0, 1.0, 128).tolist()

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        return [self.embed_text(doc) for doc in documents]


class OllamaEmbedding(BaseEmbedding):
    def embed_text(self, text: str) -> List[float]:
        # Simulates local Ollama embeddings api
        state = np.random.RandomState((sum(ord(c) for c in text) + 42) % 2**32)
        return state.normal(0.0, 1.0, 128).tolist()

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        return [self.embed_text(doc) for doc in documents]


class FutureEmbedding(BaseEmbedding):
    def embed_text(self, text: str) -> List[float]:
        state = np.random.RandomState((sum(ord(c) for c in text) + 100) % 2**32)
        return state.normal(0.0, 1.0, 128).tolist()

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        return [self.embed_text(doc) for doc in documents]
