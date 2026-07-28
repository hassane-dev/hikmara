import urllib.request
import json
import yaml
import os
from typing import List, Dict, Any
from ai_models.llm.base import BaseLLM

class OllamaEngine(BaseLLM):
    def __init__(self, model_name: str, config: Dict[str, Any] = None):
        super().__init__(model_name, config)
        self.endpoint = "http://localhost:11434"
        self.is_running = False

    def load(self) -> bool:
        self.is_running = self.check_connection()
        self.loaded = True
        return True

    def unload(self) -> bool:
        self.loaded = False
        return True

    def check_connection(self) -> bool:
        """Attempts to connect to Ollama endpoint."""
        try:
            with urllib.request.urlopen(f"{self.endpoint}/api/tags", timeout=1.0) as response:
                return response.status == 200
        except Exception:
            return False

    def get_available_models(self) -> List[str]:
        """Fetches models from Ollama or returns default list if Ollama is offline."""
        if self.check_connection():
            try:
                with urllib.request.urlopen(f"{self.endpoint}/api/tags", timeout=1.0) as response:
                    data = json.loads(response.read().decode())
                    return [m["name"] for m in data.get("models", [])]
            except Exception:
                pass
        # Fallback preset list when running locally offline / without local Ollama daemon
        return ["qwen2.5:3b", "llama3:8b", "mistral:7b", "phi3:3.8b", "gemma:2b", "deepseek-coder:1.5b"]

    def predict(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        prompt = inputs.get("prompt", "")
        system = self.config.get("system_prompt", "Vous êtes Hikmara AI.")

        # If Ollama daemon is running, try to generate a real prediction
        if self.check_connection():
            try:
                url = f"{self.endpoint}/api/generate"
                payload = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "system": system,
                    "stream": False,
                    "options": {
                        "temperature": self.config.get("temperature", 0.7)
                    }
                }
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode('utf-8'),
                    headers={'Content-Type': 'application/json'}
                )
                with urllib.request.urlopen(req, timeout=10.0) as response:
                    res_data = json.loads(response.read().decode())
                    return {"response": res_data.get("response", ""), "model": self.model_name}
            except Exception:
                pass

        # Local Offline Simulation fallback
        # Let's return a nice simulation response indicating offline status
        return {
            "response": f"En tant qu'assistant local Hikmara AI, j'ai bien pris note de votre demande concernant '{prompt}'.",
            "model": self.model_name,
            "simulated": True
        }


class TransformersEngine(BaseLLM):
    def load(self) -> bool:
        self.loaded = True
        return True
    def unload(self) -> bool:
        self.loaded = False
        return True
    def predict(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return {"response": f"[Transformers Simulation] {inputs.get('prompt')}", "model": self.model_name}
    def get_available_models(self) -> List[str]:
        return ["qwen2.5-coder-hf", "phi3-mini-hf"]


class GGUFEngine(BaseLLM):
    def load(self) -> bool:
        self.loaded = True
        return True
    def unload(self) -> bool:
        self.loaded = False
        return True
    def predict(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return {"response": f"[GGUF Llama.cpp Simulation] {inputs.get('prompt')}", "model": self.model_name}
    def get_available_models(self) -> List[str]:
        return ["llama3-8b-q4_k_m.gguf", "mistral-7b-q4_k_m.gguf"]


class FutureCloudEngine(BaseLLM):
    def load(self) -> bool:
        self.loaded = True
        return True
    def unload(self) -> bool:
        self.loaded = False
        return True
    def predict(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return {"response": f"[Future Cloud Simulation] {inputs.get('prompt')}", "model": self.model_name}
    def get_available_models(self) -> List[str]:
        return ["gpt-4o", "claude-3-opus"]


class LLMFactory:
    @staticmethod
    def create_engine(engine_type: str, model_name: str, config: Dict[str, Any] = None) -> BaseLLM:
        if engine_type == "ollama":
            return OllamaEngine(model_name, config)
        elif engine_type == "transformers":
            return TransformersEngine(model_name, config)
        elif engine_type == "gguf":
            return GGUFEngine(model_name, config)
        elif engine_type == "cloud":
            return FutureCloudEngine(model_name, config)
        else:
            return OllamaEngine(model_name, config)
