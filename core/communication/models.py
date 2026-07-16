from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

class APIRequest(BaseModel):
    module: str
    action: str
    parameters: Dict[str, Any] = Field(default_factory=dict)

class APIResponse(BaseModel):
    status: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
