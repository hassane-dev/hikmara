from pydantic import BaseModel
from typing import Optional, Any

class EventsBaseModel(BaseModel):
    """Base Pydantic model for core/events module"""
    id: Optional[str] = None
    metadata: Optional[dict] = None
