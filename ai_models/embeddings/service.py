from ai_models.base_model import BaseAIModel

class EmbeddingEngine(BaseAIModel):
    def load(self): return True
    def unload(self): return True
    def predict(self, inputs): return {"embedding": [0.1]*128}
    def status(self): return {"loaded": True}
    def get_information(self): return {"type": "Embeddings"}
