from pydantic import BaseModel
from typing import Optional, Any

class ConfigurationBaseModel(BaseModel):
    """Base Pydantic model for core/configuration module"""
    id: Optional[str] = None
    metadata: Optional[dict] = None
