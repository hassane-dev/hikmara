from pydantic import BaseModel
from typing import Optional, Any

class TasksBaseModel(BaseModel):
    """Base Pydantic model for core/tasks module"""
    id: Optional[str] = None
    metadata: Optional[dict] = None
