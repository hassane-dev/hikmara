from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class SessionStats(BaseModel):
    total_turns: int = Field(default=0, description="Nombre total d'échanges utilisateur-assistant")
    total_tokens_input: int = Field(default=0, description="Nombre estimé de tokens d'entrée traités")
    total_tokens_output: int = Field(default=0, description="Nombre estimé de tokens de sortie générés")
    average_latency: float = Field(default=0.0, description="Temps moyen de réponse de l'assistant en secondes")

class Session(BaseModel):
    session_id: str = Field(..., description="Identifiant unique de la session active")
    current_user: str = Field(default="admin", description="Utilisateur actuellement connecté")
    created_at: datetime = Field(default_factory=datetime.now, description="Horodatage de début de session")
    last_active_at: datetime = Field(default_factory=datetime.now, description="Horodatage de dernière activité")
    duration_seconds: float = Field(default=0.0, description="Durée écoulée de la session en secondes")
    is_expired: bool = Field(default=False, description="Si la session a expiré")
    statistics: SessionStats = Field(default_factory=SessionStats, description="Statistiques d'utilisation")
