import re
from typing import Dict, Any, List
from pydantic import BaseModel, Field

class TaskProfile(BaseModel):
    intent: str = Field(..., description="L'intention sémantique résolue")
    domain: str = Field(..., description="Le domaine résolu de la tâche")
    complexity: str = Field(..., description="Le niveau de complexité résolu (simple, moderate, complex, trivial)")
    risk: str = Field(..., description="L'évaluation du risque de sécurité (low, medium, high)")
    requires_agents: bool = Field(default=False, description="Indique si des agents doivent collaborer")
    recommended_agents: List[str] = Field(default_factory=list, description="Liste ordonnée d'agents recommandés")

class TaskComplexityAnalyzer:
    def __init__(self):
        pass

    def analyze_task(self, text: str, nlu_result: Any) -> TaskProfile:
        """Transforms a user query and its NLU result into a structured Task Profile (Phase 4)."""
        text_lower = text.lower().strip()

        intent = getattr(nlu_result, "intent", "unknown")
        domain = getattr(nlu_result, "domain", "general")

        # 1. Resolve security risks
        risk = "low"
        sensitive_keywords = ["execute", "run", "exécute", "install", "installe", "supprime", "delete", "format", "write", "modifier", "modify", "crée un fichier", "create file"]
        security_critical_keywords = ["audit de sécurité", "security audit", "vulnérabilité", "cryptographie", "crypto", "sensible", "mot de passe", "password", "login", "auth", "authentification", "réseau", "port"]

        if any(k in text_lower for k in security_critical_keywords):
            risk = "high"
        elif any(k in text_lower for k in sensitive_keywords):
            risk = "medium"

        # 2. Determine Complexity Level and select recommended agents
        complexity = "trivial"
        requires_agents = False
        recommended_agents = []

        # LEVEL 0: Trivial conversations / greetings or basic conceptual explanations
        is_level_0 = (intent in ["greeting", "general_conversation"]) or \
                     (intent == "explanation" and not any(k in text_lower for k in ["code", "écris", "génère", "programme", "corrige", "refactorise", "ajoute", "build", "concois", "conçois"]))

        # LEVEL 3: Full Engineering / Deep audits / Total refactoring
        is_level_3 = any(k in text_lower for k in [
            "refact", "audit de sécurité", "analyse sécurité", "systeme complet", "sécurité + performance",
            "analyse mon projet", "identifie les", "corrige-les", "écris les tests", "conçois un système", "concois un systeme"
        ]) or (risk == "high" and "audit" in text_lower)

        # LEVEL 2: Structured development (MVC, rest API, database persistence, multiple modules)
        is_level_2 = (not is_level_0 and not is_level_3) and (
            any(k in text_lower for k in ["api", "flask", "django", "sqlite", "base de données", "mvc", "interface graphique", "gui", "pyqt", "build", "concois", "conçois"]) or
            intent in ["code_modification", "code_conversion"] and any(k in text_lower for k in ["base", "sqlite", "interface", "gui"])
        )

        # LEVEL 1: Simple coding (basic function creation, single script, minor syntax correction)
        is_level_1 = (not is_level_0 and not is_level_2 and not is_level_3) and (
            intent in ["code_generation", "code_modification", "code_conversion", "explanation"] or
            any(k in text_lower for k in ["programme", "script", "fonction", "classe", "code"])
        )

        if is_level_0:
            complexity = "trivial"
            requires_agents = False
            recommended_agents = []
        elif is_level_1:
            complexity = "simple"
            requires_agents = True
            recommended_agents = ["programmer"]
        elif is_level_2:
            complexity = "moderate"
            requires_agents = True
            # Structured development requires architecture first, then code synthesis
            recommended_agents = ["architect", "programmer"]
            # Trigger Tester if test is explicitly asked or SQLite is used
            if any(k in text_lower for k in ["test", "sqlite", "base", "build"]):
                recommended_agents.append("tester")
        elif is_level_3:
            complexity = "complex"
            requires_agents = True
            # Full engineering pipeline triggers specialized agents based on user keywords
            recommended_agents = ["architect", "programmer"]
            if any(k in text_lower for k in ["sécurité", "audit", "auth"]):
                recommended_agents.append("security")
            if any(k in text_lower for k in ["test", "valide", "refact", "corrige"]):
                recommended_agents.append("tester")
            if any(k in text_lower for k in ["doc", "documente", "refact"]):
                recommended_agents.append("docs")

            # Default fallback for full lifecycle if general refactor
            if len(recommended_agents) <= 2:
                recommended_agents.extend(["tester", "security", "docs"])

        # Override for specific security command (Test case: Audite mon application niveau sécurité)
        if "sécurité" in text_lower and "audit" in text_lower:
            if "security" not in recommended_agents:
                recommended_agents.append("security")

        return TaskProfile(
            intent=intent,
            domain=domain,
            complexity=complexity,
            risk=risk,
            requires_agents=requires_agents,
            recommended_agents=recommended_agents
        )

global_task_complexity_analyzer = TaskComplexityAnalyzer()
