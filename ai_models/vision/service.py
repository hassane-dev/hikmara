from ai_models.base_model import BaseAIModel

class VisionEngine(BaseAIModel):
    def load(self): return True
    def unload(self): return True
    def predict(self, inputs): return {"objects": ["screen"], "ocr_text": "Error in db"}
    def status(self): return {"loaded": True}
    def get_information(self): return {"type": "Vision"}
