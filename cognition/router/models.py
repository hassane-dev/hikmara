from pydantic import BaseModel, Field
from typing import List

class RoutingDecision(BaseModel):
    intent: str = Field(..., description="L'intention détectée (ex: Salutations, Conversation générale, Commandes système, Développement logiciel, etc.)")
    domain: str = Field(..., description="Le domaine de la requête (ex: conversation, python, php, system, tools, general, etc.)")
    complexity: str = Field(..., description="L'évaluation de la complexité de la requête (trivial, simple, moderate, complex, critical)")
    language: str = Field(..., description="La langue détectée (ex: fr, en)")
    pipeline: str = Field(..., description="Le pipeline d'exécution recommandé")
    requires_model: bool = Field(..., description="Si la requête nécessite un LLM local")
    requires_tools: bool = Field(..., description="Si la requête nécessite l'utilisation d'outils")
    requires_agents: bool = Field(..., description="Si la requête nécessite l'activation du système multi-agents")
    requires_memory: bool = Field(..., description="Si la requête nécessite l'accès à la mémoire/contexte")
    safety_level: str = Field(..., description="Niveau de risque/sécurité (ex: normal, sensitive)")
    agents_to_trigger: List[str] = Field(default_factory=list, description="Les agents à activer si applicable")
    justification: str = Field(..., description="Justification de la décision de routage")
    confidence: float = Field(1.0, description="Le niveau de confiance, de 0.0 à 1.0")

    # Compatibility properties
    @property
    def category(self) -> str:
        return self.intent

    @property
    def recommended_pipeline(self) -> str:
        # Map Phase 2 pipeline names to Phase 1.5 pipeline names for 100% backward compatibility
        if self.pipeline in ["direct_conversation", "conversation", "coding_conversation"]:
            return "Conversation"
        elif self.pipeline == "system_commands":
            return "Commandes système"
        elif self.pipeline == "tools":
            return "Outils"
        elif self.pipeline == "agent_task":
            if self.intent == "Requêtes complexes":
                return "Requêtes complexes"
            return "Développement logiciel"
        return "Conversation"

class IntentResult(RoutingDecision):
    # Backward compatibility subclass
    pass
