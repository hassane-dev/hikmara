import urllib.request
import json
import yaml
import os
import time
from typing import List, Dict, Any, Iterator
from ai_models.llm.base import BaseLLM
from ai_models.llm.models import LLMResponse, ToolCall, ToolResult

class OllamaEngine(BaseLLM):
    def __init__(self, model_name: str, config: Dict[str, Any] = None):
        super().__init__(model_name, config)
        self.endpoint = "http://localhost:11434"
        self.is_running = False

    def load_model(self) -> bool:
        self.is_running = self.check_connection()
        self.loaded = True
        return True

    def unload_model(self) -> bool:
        self.loaded = False
        return True

    def check_connection(self) -> bool:
        """Attempts to connect to Ollama endpoint."""
        try:
            with urllib.request.urlopen(f"{self.endpoint}/api/tags", timeout=1.0) as response:
                return response.status == 200
        except Exception:
            return False

    def list_models(self) -> List[str]:
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

    def get_available_models(self) -> List[str]:
        return self.list_models()

    def generate(self, prompt: str, system: str = "") -> LLMResponse:
        start_time = time.time()

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
                    text = res_data.get("response", "")
                    latency = time.time() - start_time
                    return LLMResponse(
                        text=text,
                        markdown=text,
                        latency=round(latency, 4),
                        model=self.model_name,
                        tokens_input=len(prompt) // 4,
                        tokens_output=len(text) // 4,
                        finish_reason="stop"
                    )
            except Exception:
                pass

        # Offline Mock Fallback Simulation
        latency = time.time() - start_time
        sim_response = f"En tant qu'assistant local Hikmara AI, j'ai bien pris note de votre demande : '{prompt}'."
        return LLMResponse(
            text=sim_response,
            markdown=sim_response,
            latency=round(latency, 4),
            model=self.model_name,
            tokens_input=len(prompt) // 4,
            tokens_output=len(sim_response) // 4,
            finish_reason="stop",
            metadata={"simulated": True}
        )

    def generate_stream(self, prompt: str, system: str = "") -> Iterator[LLMResponse]:
        # Return generator containing single complete response (minimal streaming)
        yield self.generate(prompt, system)

    def health_check(self) -> bool:
        return self.check_connection()

    def switch_model(self, model_name: str) -> bool:
        self.model_name = model_name
        return True

    def supports_streaming(self) -> bool:
        return True

    def supports_tools(self) -> bool:
        return False


class TransformersEngine(BaseLLM):
    def load_model(self) -> bool:
        self.loaded = True
        return True
    def unload_model(self) -> bool:
        self.loaded = False
        return True
    def generate(self, prompt: str, system: str = "") -> LLMResponse:
        reply = f"[Transformers HF Simulation] {prompt}"
        return LLMResponse(text=reply, markdown=reply, model=self.model_name)
    def generate_stream(self, prompt: str, system: str = "") -> Iterator[LLMResponse]:
        yield self.generate(prompt, system)
    def health_check(self) -> bool:
        return True
    def list_models(self) -> List[str]:
        return ["qwen2.5-coder-hf", "phi3-mini-hf"]
    def switch_model(self, model_name: str) -> bool:
        self.model_name = model_name
        return True
    def supports_streaming(self) -> bool:
        return False
    def supports_tools(self) -> bool:
        return False
    def get_available_models(self) -> List[str]:
        return self.list_models()


class GGUFEngine(BaseLLM):
    def load_model(self) -> bool:
        self.loaded = True
        return True
    def unload_model(self) -> bool:
        self.loaded = False
        return True
    def generate(self, prompt: str, system: str = "") -> LLMResponse:
        reply = f"[GGUF llama.cpp Simulation] {prompt}"
        return LLMResponse(text=reply, markdown=reply, model=self.model_name)
    def generate_stream(self, prompt: str, system: str = "") -> Iterator[LLMResponse]:
        yield self.generate(prompt, system)
    def health_check(self) -> bool:
        return True
    def list_models(self) -> List[str]:
        return ["llama3-8b-q4_k_m.gguf", "mistral-7b-q4_k_m.gguf"]
    def switch_model(self, model_name: str) -> bool:
        self.model_name = model_name
        return True
    def supports_streaming(self) -> bool:
        return False
    def supports_tools(self) -> bool:
        return False
    def get_available_models(self) -> List[str]:
        return self.list_models()


class FutureCloudEngine(BaseLLM):
    def load_model(self) -> bool:
        self.loaded = True
        return True
    def unload_model(self) -> bool:
        self.loaded = False
        return True
    def generate(self, prompt: str, system: str = "") -> LLMResponse:
        reply = f"[Cloud Engine Simulation] {prompt}"
        return LLMResponse(text=reply, markdown=reply, model=self.model_name)
    def generate_stream(self, prompt: str, system: str = "") -> Iterator[LLMResponse]:
        yield self.generate(prompt, system)
    def health_check(self) -> bool:
        return True
    def list_models(self) -> List[str]:
        return ["gpt-4o", "claude-3-opus"]
    def switch_model(self, model_name: str) -> bool:
        self.model_name = model_name
        return True
    def supports_streaming(self) -> bool:
        return False
    def supports_tools(self) -> bool:
        return False
    def get_available_models(self) -> List[str]:
        return self.list_models()


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
