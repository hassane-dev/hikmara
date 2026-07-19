from pydantic import BaseModel, Field
from typing import Dict, Any

class LanguageUnderstandingResult(BaseModel):
    text: str = Field(..., description="Le texte original de la requête utilisateur")
    language: str = Field(..., description="La langue détectée (ex: fr, en)")
    intent: str = Field(..., description="L'intention détectée (ex: greeting, general_conversation, code_generation, code_modification, explanation, code_conversion, system, tools, unknown)")
    domain: str = Field(..., description="Le domaine technique ou fonctionnel de la requête (ex: python, php, database, system, tools, conversation, general)")
    entities: Dict[str, Any] = Field(default_factory=dict, description="Entités clés extraites de la requête")
    confidence: float = Field(..., description="Le score de confiance de l'analyse, de 0.0 à 1.0")
    is_follow_up: bool = Field(default=False, description="Si la requête fait référence à une étape précédente ou un suivi")
    references_previous_context: bool = Field(default=False, description="Si la requête fait explicitement référence au contexte ou au code précédent")
