from pydantic import BaseModel
from typing import Optional, Any

class SystemBaseModel(BaseModel):
    """Base Pydantic model for core/system module"""
    id: Optional[str] = None
    metadata: Optional[dict] = None
