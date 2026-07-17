from pydantic import BaseModel
from typing import Optional, Any

class SecurityBaseModel(BaseModel):
    """Base Pydantic model for core/security module"""
    id: Optional[str] = None
    metadata: Optional[dict] = None
