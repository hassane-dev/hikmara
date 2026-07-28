from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ConversationContext(BaseModel):
    messages: List[Dict[str, Any]] = Field(default_factory=list, description="Messages récents")
    previous_intents: List[str] = Field(default_factory=list, description="Intentions précédentes")
    previous_routing_decisions: List[Dict[str, Any]] = Field(default_factory=list, description="Décisions de routage précédentes")
    detected_entities: Dict[str, Any] = Field(default_factory=dict, description="Entités détectées")
    active_domain: Optional[str] = Field(None, description="Domaine actif (ex: python, php)")
    language: str = Field("fr", description="Langue de la conversation")
    context_references: Dict[str, Any] = Field(default_factory=dict, description="Références contextuelles (ex: code généré précédemment)")
    current_topic: Optional[str] = Field(None, description="Le sujet ou thème courant de la discussion")
    file_references: List[str] = Field(default_factory=list, description="Liste des fichiers référencés")
    memory_references: Dict[str, Any] = Field(default_factory=dict, description="Références mémoire à court/long terme")
    previous_responses: List[str] = Field(default_factory=list, description="Historique des réponses de l'assistant")
