import numpy as np

class SimpleVectorStore:
    def __init__(self):
        self._store = []

    def add_vector(self, text, vector, metadata=None):
        self._store.append({
            "text": text,
            "vector": np.array(vector, dtype=np.float32),
            "metadata": metadata or {}
        })

    def search(self, query_vector, top_k=3):
        if not self._store: return []
        q_v = np.array(query_vector, dtype=np.float32)
        norm_q = np.linalg.norm(q_v)
        if norm_q == 0: return []
        results = []
        for item in self._store:
            v = item["vector"]
            norm_v = np.linalg.norm(v)
            similarity = float(np.dot(q_v, v) / (norm_q * norm_v)) if norm_v != 0 else 0.0
            results.append((item["text"], similarity, item["metadata"]))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def clear(self):
        self._store.clear()

global_vector_store = SimpleVectorStore()
