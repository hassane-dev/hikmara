from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class ModelSpecs(BaseModel):
    id: str = Field(..., description="Unique model identifier")
    name: str = Field(..., description="Display name of the model")
    family: str = Field(..., description="Model family, e.g., Qwen, Llama, Mistral, Phi")
    engine: str = Field(..., description="Target execution engine, e.g., ollama, gguf, transformers, cloud")
    size_gb: float = Field(0.0, description="Size on disk in Gigabytes")
    parameters: str = Field("", description="Parameter size expression, e.g., 3B, 8B, 14B")
    max_context: int = Field(2048, description="Maximum context length tokens")
    streaming: bool = Field(True, description="Whether the model supports streaming generation")
    vision: bool = Field(False, description="Whether the model supports vision inputs")
    audio: bool = Field(False, description="Whether the model supports audio processing")
    tools: bool = Field(False, description="Whether the model supports function / tool calling")
    embeddings: bool = Field(False, description="Whether this is an embedding model")
    gpu_required: bool = Field(False, description="Whether GPU is required for execution")
    ram_estimated_gb: float = Field(4.0, description="Estimated RAM needed for inference")
    speed_tps: float = Field(0.0, description="Estimated speed in tokens per second")
    precision: str = Field("q4_K_M", description="Quantization precision or format")
    license: str = Field("unknown", description="Open-source or commercial license")
    installed: bool = Field(True, description="Whether the model is downloaded/installed locally")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata attributes")

    # Phase 5.1 properties & compatibility fields
    @property
    def model_id(self) -> str:
        return self.id

    @property
    def model_version(self) -> str:
        return self.metadata.get("model_version", "1.0.0")

    @property
    def architecture_version(self) -> str:
        return self.metadata.get("architecture_version", "1.0.0")

    @property
    def model_hash(self) -> str:
        return self.metadata.get("model_hash", f"hash_{self.id}_mock")

    @property
    def tokenizer_hash(self) -> str:
        return self.metadata.get("tokenizer_hash", f"tokenizer_{self.id}_mock")

    @property
    def engine_type(self) -> str:
        return self.engine

    @property
    def modality(self) -> str:
        if self.vision:
            return "vision"
        if self.audio:
            return "audio"
        if self.embeddings:
            return "embedding"
        return "text"

    @property
    def file_size(self) -> float:
        return self.size_gb

    @property
    def required_memory(self) -> float:
        return self.ram_estimated_gb

    @property
    def supported_context_window(self) -> int:
        return self.max_context
