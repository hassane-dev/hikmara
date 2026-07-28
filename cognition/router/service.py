import re
from typing import List, Dict, Any
from cognition.router.models import RoutingDecision
from cognition.nlu.service import global_language_understanding
from cognition.context.service import global_context_manager
from cognition.router.tool_router import global_tool_router
from cognition.router.agent_router import global_agent_router
from cognition.router.capability_router import global_capability_router

class IntentRouter:
    # Categories constants
    CONVERSATION_GENERALE = "Conversation générale"
    SALUTATIONS = "Salutations"
    DEVELOPPEMENT_LOGICIEL = "Développement logiciel"
    GENERATION_CODE = "Génération de code"
    ANALYSE_CODE = "Analyse de code"
    EXPLICATION_CODE = "Explication de code"
    QUESTIONS_TECHNIQUES = "Questions techniques"
    COMMANDES_SYSTEME = "Commandes système"
    GESTION_OUTILS = "Gestion des outils"
    RECHERCHE_INFORMATIONS = "Recherche d'informations"
    SECURITE = "Sécurité"
    REQUETES_COMPLEXES = "Requêtes complexes"
    INCONNU = "Inconnu"

    def __init__(self):
        pass

    def route(self, prompt: str) -> RoutingDecision:
        """Analyzes a user prompt using NLU, ToolRouter, AgentRouter, and CapabilityRouter."""
        prompt_lower = prompt.strip().lower()

        # 1. Invoke independent Language Understanding (NLU) Layer (Phase 2.5)
        # Absolutely no regex is done inside IntentRouter.
        nlu = global_language_understanding.analyze(prompt)

        # 2. Retrieve current conversation context
        context = global_context_manager.get_context()

        # 3. Determine main intent category based on NLU result
        intent = self.INCONNU
        if nlu.intent == "greeting":
            intent = self.SALUTATIONS
        elif nlu.intent == "general_conversation":
            intent = self.CONVERSATION_GENERALE
        elif nlu.intent == "system":
            intent = self.COMMANDES_SYSTEME
        elif nlu.intent == "tools":
            intent = self.GESTION_OUTILS
        elif nlu.intent == "explanation":
            intent = self.EXPLICATION_CODE
        elif nlu.intent in ["code_generation", "code_modification", "code_conversion"]:
            # Check if this task involves structural components or integrations
            if nlu.domain in ["api", "database", "system"] or any(k in prompt_lower for k in ["api", "flask", "django", "server", "serveur", "web app", "integration"]):
                intent = self.DEVELOPPEMENT_LOGICIEL
            else:
                intent = self.GENERATION_CODE

        # Map keyword overrides from NLU
        if "base de données" in prompt_lower or "database" in prompt_lower:
            if nlu.intent == "explanation":
                intent = self.QUESTIONS_TECHNIQUES
            elif nlu.intent in ["code_generation", "code_modification"]:
                intent = self.DEVELOPPEMENT_LOGICIEL
        if "api flask" in prompt_lower or "api" in prompt_lower:
            intent = self.DEVELOPPEMENT_LOGICIEL

        if "sécurité" in prompt_lower or "security" in prompt_lower or "vulnerability" in prompt_lower:
            intent = self.SECURITE

        if "conçois un système complet" in prompt_lower or "orchestre un developpement complexe" in prompt_lower:
            intent = self.REQUETES_COMPLEXES

        # Resolve domain (taking context into account)
        domain = nlu.domain
        if nlu.is_follow_up or nlu.intent in ["code_modification", "code_conversion"]:
            if nlu.domain in ["general", "conversation"] and context.active_domain:
                domain = context.active_domain

        # 5. Determine Complexity
        is_complex_prompt = any(k in prompt_lower for k in [
            "analyse mon projet", "identifie les problèmes", "corrige-les", "écris les tests", "conçois un système complet",
            "analyse tout mon projet", "corrige les problèmes de sécurité", "orchestre un developpement complexe"
        ])
        is_structural_or_dev = intent in [self.DEVELOPPEMENT_LOGICIEL, self.GENERATION_CODE] or any(k in prompt_lower for k in ["api", "flask", "django", "database", "base de données", "integration", "active record", "classe", "class", "method", "méthode"])

        if nlu.intent in ["greeting", "general_conversation"]:
            complexity = "trivial"
        elif is_complex_prompt or "conçois un système" in prompt_lower or "orchestre" in prompt_lower:
            complexity = "complex"
        elif is_structural_or_dev:
            # Simple addition requests
            if any(k in prompt_lower for k in ["somme de deux entiers", "additionne deux", "calculer la somme"]):
                complexity = "simple"
            else:
                complexity = "moderate"
        else:
            if len(prompt_lower) > 100 or "sqlite" in prompt_lower or "interface graphique" in prompt_lower or "api rest" in prompt_lower:
                complexity = "moderate"
            else:
                complexity = "simple"

        # 6. Delegate specialized checks to routers
        tools_decision = global_tool_router.decide_tools(prompt)
        agents_decision = global_agent_router.decide_agents(prompt, intent, complexity)

        requires_tools = tools_decision["needs_tools"] or nlu.intent == "tools" or any(k in prompt_lower for k in ["pip", "npm", "package", "dependency", "installe", "outil", "tool", "file", "fichier", "run", "exécute"])
        requires_agents = agents_decision["requires_agents"]
        agents_to_trigger = agents_decision["agents_to_trigger"]

        requires_model = nlu.intent in ["general_conversation", "code_generation", "code_modification", "code_conversion", "explanation"] or intent in [self.SALUTATIONS, self.CONVERSATION_GENERALE, self.GENERATION_CODE, self.DEVELOPPEMENT_LOGICIEL, self.EXPLICATION_CODE]
        requires_memory = nlu.is_follow_up or nlu.references_previous_context or bool(context.active_domain)

        # 7. Pipeline resolution
        if complexity == "trivial":
            pipeline = "direct_conversation"
        elif requires_agents:
            pipeline = "agent_task"
        elif nlu.intent == "system":
            pipeline = "system_commands"
        elif nlu.intent == "tools":
            pipeline = "tools"
        elif intent in [self.GENERATION_CODE, self.DEVELOPPEMENT_LOGICIEL, self.EXPLICATION_CODE] and complexity == "simple":
            pipeline = "coding_conversation"
        elif intent in [self.GENERATION_CODE, self.DEVELOPPEMENT_LOGICIEL] and complexity == "moderate":
            if requires_memory:
                pipeline = "coding_conversation"
            else:
                pipeline = "agent_task"
        else:
            pipeline = "conversation"

        justification = f"Décision d'orchestration basée sur l'analyse NLU (intention={nlu.intent}, confiance={nlu.confidence})."

        return RoutingDecision(
            intent=intent,
            domain=domain,
            complexity=complexity,
            language=nlu.language,
            pipeline=pipeline,
            requires_model=requires_model,
            requires_tools=requires_tools,
            requires_agents=requires_agents,
            requires_memory=requires_memory,
            safety_level="sensitive" if requires_tools or "exécute" in prompt_lower or not tools_decision["security_authorized"] else "normal",
            agents_to_trigger=agents_to_trigger,
            justification=justification,
            confidence=nlu.confidence
        )

global_intent_router = IntentRouter()
