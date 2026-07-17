from pydantic import BaseModel
from typing import Optional, Any

class LoggingBaseModel(BaseModel):
    """Base Pydantic model for core/logging module"""
    id: Optional[str] = None
    metadata: Optional[dict] = None
