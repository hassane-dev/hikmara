from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class ModelManagerStats(BaseModel):
    active_engine: str
    active_model: str
    ram_usage_gb: float = 0.0
    vram_usage_gb: float = 0.0
