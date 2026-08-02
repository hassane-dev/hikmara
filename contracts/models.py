from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum

class Capability(str, Enum):
    TEXT_GENERATION = "text_generation"
    VISION = "vision"
    EMBEDDING = "embedding"
    TOOL_CALLING = "tool_calling"
    STREAMING = "streaming"
    JSON_OUTPUT = "json_output"
    AUDIO_INPUT = "audio_input"

class ModalityType(str, Enum):
    TEXT = "text"
    VISION = "vision"
    AUDIO = "audio"
    EMBEDDING = "embedding"

class ComputeDeviceType(str, Enum):
    CPU = "cpu"
    CUDA = "cuda"
    ROCM = "rocm"
    METAL = "metal"
    NPU = "npu"

class ComputeDevice(BaseModel):
    schema_version: int = 1
    device_id: int
    device_type: ComputeDeviceType
    total_memory_gb: float
    free_memory_gb: float
    utilization_percent: float

class TaskExecutionPlan(BaseModel):
    schema_version: int = 1
    complexity: str               # "trivial", "simple", "moderate", "complex"
    expected_output_size: str     # "small", "medium", "large"
    accuracy_priority: bool       # True/False
    persistence_required: bool    # True/False
    modality: str                 # "text", "vision", "audio", "embedding"

class InferenceProfile(BaseModel):
    schema_version: int = 1
    model_id: str
    context_window: int
    temperature: float
    max_tokens: int
    engine_type: str
    required_capabilities: List[Capability] = Field(default_factory=list)

class KVCacheKey(BaseModel):
    schema_version: int = 1
    session_id: str
    project_id: str
    model_hash: str
    system_hash: str
    template_version: str
    tokenizer_hash: str
    context_window: int
    generation_id: str
    security_scope_hash: str

class WorkspaceFile(BaseModel):
    schema_version: int = 1
    path: str
    file_hash: str
    modified_at: float

class WorkspaceContext(BaseModel):
    schema_version: int = 1
    workspace_id: str
    project_id: str
    active_files: List[WorkspaceFile] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    context_version: int = 1

class EnergyMetrics(BaseModel):
    schema_version: int = 1
    cpu_seconds: float
    estimated_wh: float
    battery_consumption: float

class InferenceMetrics(BaseModel):
    schema_version: int = 1
    model_active: str
    ram_usage: float
    cpu_usage: float
    ttft: float
    tokens_second: float
    kv_hit_rate: float
    loaded_models: List[str] = Field(default_factory=list)
    energy: Optional[EnergyMetrics] = None

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"

class HealthReport(BaseModel):
    schema_version: int = 1
    status: HealthStatus
    engine_loaded: bool
    hot_pool_count: int
    ram_available_gb: float
    device_status: str
    cache_integrity: bool
    active_warnings: List[str] = Field(default_factory=list)
    timestamp: float

class PerformanceProfile(str, Enum):
    AUTO = "auto"
    BALANCED = "balanced"
    LOW_POWER = "low_power"
    MAX_PERFORMANCE = "max_perf"

class TraceContext(BaseModel):
    schema_version: int = 1
    request_id: str
    session_id: str
    workspace_id: str
    generation_id: str
    parent_request: Optional[str] = None
    created_at: float

class RuntimeContext(BaseModel):
    schema_version: int = 1
    session_id: str
    workspace_context: Optional[WorkspaceContext] = None
    security_context: Optional[Any] = None
    performance_profile: PerformanceProfile = PerformanceProfile.BALANCED
    active_device: Optional[ComputeDevice] = None
    trace_context: Optional[TraceContext] = None
