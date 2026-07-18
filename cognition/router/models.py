from pydantic import BaseModel, Field
from typing import List

class IntentResult(BaseModel):
    category: str = Field(..., description="La catégorie d'intention détectée")
    confidence: float = Field(..., description="Le niveau de confiance, de 0.0 à 1.0")
    recommended_pipeline: str = Field(..., description="Le pipeline d'exécution recommandé")
    agents_to_trigger: List[str] = Field(default_factory=list, description="Les agents à activer pour ce pipeline")
    justification: str = Field(..., description="Justification de la décision")
