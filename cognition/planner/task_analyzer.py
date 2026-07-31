import re
from typing import Dict, Any, List
from pydantic import BaseModel, Field

class TaskProfile(BaseModel):
    intent: str = Field(..., description="L'intention sémantique résolue")
    domain: str = Field(..., description="Le domaine résolu de la tâche")
    complexity: str = Field(..., description="Le niveau de complexité résolu (simple, moderate, complex, trivial)")
    risk: str = Field(..., description="L'évaluation du risque de sécurité (low, medium, high)")
    requires_agents: bool = Field(default=False, description="Indique si des agents doivent collaborer")
    recommended_agents: List[str] = Field(default_factory=list, description="Liste ordonnée d'agents recommandés (recommandations neutres)")
    deliverables: List[str] = Field(default_factory=list, description="Livrables attendus (ex: code, architecture, tests, doc, audit)")
    scope: str = Field(default="module", description="Portée de la demande (single_function, module, system, full_project)")
    functional_needs: List[str] = Field(default_factory=list, description="Besoins fonctionnels détectés")

def has_word(text: str, keywords: List[str]) -> bool:
    """Helper to safely check if text contains any of the keywords as distinct words, avoiding substring issues."""
    for kw in keywords:
        pattern = r"\b" + re.escape(kw) + r"\b"
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

class TaskComplexityAnalyzer:
    def __init__(self):
        pass

    def analyze_task(self, text: str, nlu_result: Any) -> TaskProfile:
        """
        Transforms a user query and its NLU result into a structured, agent-neutral Task Profile (Phase 4).
        This analyzer does not depend on any agent availability, routers, or PromptBuilder.
        """
        text_lower = text.lower().strip()

        intent = getattr(nlu_result, "intent", "unknown")
        domain = getattr(nlu_result, "domain", "general")

        # 1. Resolve security risks and functional needs
        risk = "low"
        sensitive_keywords = ["execute", "run", "exécute", "install", "installe", "supprime", "delete", "format", "write", "modifier", "modify", "crée un fichier", "create file"]
        security_critical_keywords = ["audit de sécurité", "security audit", "vulnérabilité", "cryptographie", "crypto", "sensible", "mot de passe", "password", "login", "auth", "authentification", "réseau", "port"]

        if has_word(text_lower, security_critical_keywords) or any(k in text_lower for k in ["audit de sécurité", "security audit"]):
            risk = "high"
        elif has_word(text_lower, sensitive_keywords) or any(k in text_lower for k in ["crée un fichier", "create file"]):
            risk = "medium"

        # 2. Extract deliverables
        deliverables = []
        if has_word(text_lower, ["test", "valide", "vérifie", "check", "assert", "unitaire", "tests"]):
            deliverables.append("tests")
        if has_word(text_lower, ["conçois", "concois", "architecture", "conception", "blueprint", "plan", "conçoit"]):
            deliverables.append("architecture")
        if has_word(text_lower, ["sécurité", "security", "audit", "vulnérabilité"]) or "audit de sécurité" in text_lower:
            deliverables.append("security_audit")
        if has_word(text_lower, ["doc", "documente", "explication", "explique", "documentation"]):
            deliverables.append("documentation")
        if has_word(text_lower, ["écris", "génère", "programme", "corrige", "refactorise", "ajoute", "build", "code", "fonction", "classe", "script"]):
            deliverables.append("code")

        # 3. Extract Scope (Portée)
        scope = "module"
        if any(k in text_lower for k in ["projet complet", "système complet", "système", "application complète", "mon projet", "mon application"]):
            scope = "full_project"
        elif has_word(text_lower, ["fonction", "script", "corrige", "bug"]):
            scope = "single_function"

        # 4. Extract Functional Needs
        functional_needs = []
        if has_word(text_lower, ["sqlite", "database", "postgresql", "mysql", "persistence"]) or "base de données" in text_lower:
            functional_needs.append("persistence")
        if has_word(text_lower, ["gui", "pyqt", "pyqt6", "react", "html", "css"]) or "interface graphique" in text_lower:
            functional_needs.append("ui")
        if has_word(text_lower, ["flask", "django", "laravel", "endpoint", "rest"]) or "api" in text_lower:
            functional_needs.append("api")
        if has_word(text_lower, ["sécurité", "security", "auth", "crypt", "chiffrement"]):
            functional_needs.append("security_hardening")

        # 5. Determine Complexity Level
        # Trivial: conversation, greeting, system utility commands, tool management, or basic conceptual explanation
        is_level_0 = (intent in ["greeting", "general_conversation"]) or \
                     (intent in ["system", "tools"]) or \
                     (intent == "explanation" and not deliverables) or \
                     (intent == "unknown" and not deliverables and not functional_needs)

        # Complex: large projects, deep audits, full system design
        is_level_3 = (scope == "full_project") or \
                     (risk == "high" and "audit" in text_lower) or \
                     any(k in text_lower for k in ["systeme complet", "sécurité + performance", "analyse mon projet", "refactorise mon projet"])

        # Moderate: structured development (e.g. APIs, persistence layer, multi-module script)
        is_level_2 = (not is_level_0 and not is_level_3) and (
            len(functional_needs) >= 1 or
            len(deliverables) >= 2 or
            any(k in text_lower for k in ["api", "concois", "conçois", "build"])
        )

        # Simple: basic code, simple script, single function, or explanation of code
        is_level_1 = (not is_level_0 and not is_level_2 and not is_level_3)

        if is_level_0:
            complexity = "trivial"
        elif is_level_1:
            complexity = "simple"
        elif is_level_2:
            complexity = "moderate"
        else:
            complexity = "complex"

        # Set requires_agents and recommended_agents based purely on NEUTRAL task attributes,
        # without hardcoding technology-based triggers (like sqlite triggers tester).
        requires_agents = (complexity != "trivial")
        recommended_agents = []

        if complexity == "simple":
            recommended_agents = ["programmer"]
        elif complexity == "moderate":
            # For moderate development, suggest architecture & code
            recommended_agents = ["architect", "programmer"]
        elif complexity == "complex":
            # For complex tasks, the baseline involves design & implementation
            recommended_agents = ["architect", "programmer"]

        return TaskProfile(
            intent=intent,
            domain=domain,
            complexity=complexity,
            risk=risk,
            requires_agents=requires_agents,
            recommended_agents=recommended_agents,
            deliverables=deliverables,
            scope=scope,
            functional_needs=functional_needs
        )

global_task_complexity_analyzer = TaskComplexityAnalyzer()
