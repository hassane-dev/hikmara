from pydantic import BaseModel
from typing import Optional, Any

class ApiBaseModel(BaseModel):
    """Base Pydantic model for core/api module"""
    id: Optional[str] = None
    metadata: Optional[dict] = None
