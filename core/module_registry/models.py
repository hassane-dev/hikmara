from pydantic import BaseModel
from typing import Optional, Any

class Module_registryBaseModel(BaseModel):
    """Base Pydantic model for core/module_registry module"""
    id: Optional[str] = None
    metadata: Optional[dict] = None
