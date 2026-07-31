from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class WorkContext(BaseModel):
    """
    Independent active working memory (Work Context) representing the current task/project.
    Resets or archives upon domain/subject shift to prevent leakage.
    """
    active_domain: Optional[str] = Field(None, description="Domaine actif (ex: python, php)")
    language: str = Field("fr", description="Langue courante de travail")
    technologies: List[str] = Field(default_factory=list, description="Technologies actives (ex: PyQt6, SQLite)")
    context_references: Dict[str, Any] = Field(default_factory=dict, description="Références techniques, comme last_generated_code")
    file_references: List[str] = Field(default_factory=list, description="Fichiers actuellement manipulés")
    current_topic: Optional[str] = Field(None, description="Sujet ou intention technique courante")

class ConversationContext(BaseModel):
    """
    Main Conversation Context representing the entire session.
    Features strict separation between conversation memory and active work context.
    """
    messages: List[Dict[str, Any]] = Field(default_factory=list, description="Messages récents (Mémoire Conversationnelle)")
    previous_intents: List[str] = Field(default_factory=list, description="Intentions de conversation précédentes")
    previous_routing_decisions: List[Dict[str, Any]] = Field(default_factory=list, description="Décisions de routage précédentes")
    detected_entities: Dict[str, Any] = Field(default_factory=dict, description="Entités détectées globalement")

    # Backwards-compatible attributes mapped to work_context
    active_domain: Optional[str] = Field(None, description="Domaine actif")
    language: str = Field("fr", description="Langue de la conversation")
    context_references: Dict[str, Any] = Field(default_factory=dict, description="Références contextuelles actives")
    current_topic: Optional[str] = Field(None, description="Sujet ou thème de discussion")
    file_references: List[str] = Field(default_factory=list, description="Fichiers référencés")
    memory_references: Dict[str, Any] = Field(default_factory=dict, description="Références mémoire à court/long terme")
    previous_responses: List[str] = Field(default_factory=list, description="Historique des réponses de l'assistant")

    # Phase 3 structures
    user_preferences: Dict[str, Any] = Field(default_factory=dict, description="Préférences utilisateur transversales (style, etc.)")
    active_work_context: WorkContext = Field(default_factory=WorkContext, description="Mémoire de travail active (Work Context)")
    archived_contexts: List[Dict[str, Any]] = Field(default_factory=list, description="Mémoires de travail archivées")
