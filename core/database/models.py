from pydantic import BaseModel
from typing import Optional, Any

class DatabaseBaseModel(BaseModel):
    """Base Pydantic model for core/database module"""
    id: Optional[str] = None
    metadata: Optional[dict] = None
