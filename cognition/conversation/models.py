from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

class ModelRequest(BaseModel):
    prompt: str = Field(..., description="Le prompt de l'utilisateur")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Contexte additionnel pour le modèle")

class ModelResponse(BaseModel):
    response: str = Field(..., description="La réponse générée par le modèle")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Métadonnées sur l'exécution ou le modèle utilisé")
