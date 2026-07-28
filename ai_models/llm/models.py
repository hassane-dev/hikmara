from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

class ToolCall(BaseModel):
    id: str = Field(..., description="Identifiant unique de l'appel d'outil")
    name: str = Field(..., description="Nom de l'outil à exécuter")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Arguments à passer à l'outil")

class ToolResult(BaseModel):
    call_id: str = Field(..., description="ID de l'appel d'outil correspondant")
    status: str = Field(..., description="Statut de l'exécution (success, error)")
    output: str = Field(..., description="Résultat de l'exécution")

class LLMResponse(BaseModel):
    text: str = Field(..., description="Texte brut généré par le modèle")
    markdown: str = Field(..., description="Réponse formatée en Markdown")
    code: Optional[str] = Field(None, description="Extrait de code généré si applicable")
    language: Optional[str] = Field(None, description="Langage du code généré (ex: python, php)")
    citations: List[str] = Field(default_factory=list, description="Liste des citations de documents ou fichiers consultés")
    confidence: float = Field(1.0, description="Score de confiance du modèle sur sa génération")
    tokens_input: int = Field(0, description="Estimation de la consommation de tokens d'entrée")
    tokens_output: int = Field(0, description="Estimation de la consommation de tokens de sortie")
    latency: float = Field(0.0, description="Latence de génération en secondes")
    model: str = Field(..., description="Identifiant du modèle de langage utilisé")
    finish_reason: str = Field("stop", description="Raison de la fin de génération (stop, length, tool_calls, etc.)")
    tool_calls: List[ToolCall] = Field(default_factory=list, description="Appels d'outils requis par le modèle")
    reasoning: Optional[str] = Field(None, description="Chaîne de réflexion / Raisonnement interne du modèle")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Métadonnées supplémentaires")
