import re
from typing import List, Callable, Dict, Any
from cognition.router.models import RoutingDecision, IntentResult

class RoutingRule:
    def __init__(self, category: str, matcher: Callable[[str], bool], confidence: float, recommended_pipeline: str, agents_to_trigger: List[str], justification: str):
        self.category = category
        self.matcher = matcher
        self.confidence = confidence
        self.recommended_pipeline = recommended_pipeline
        self.agents_to_trigger = agents_to_trigger
        self.justification = justification

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
        self._rules: List[RoutingRule] = []
        self._setup_default_rules()

    def register_rule(self, category: str, matcher: Callable[[str], bool], confidence: float, recommended_pipeline: str, agents_to_trigger: List[str], justification: str):
        """Allows registering a new routing rule dynamically, adding it to the top of evaluation list."""
        rule = RoutingRule(category, matcher, confidence, recommended_pipeline, agents_to_trigger, justification)
        self._rules.insert(0, rule)  # Newer rules take precedence

    def _setup_default_rules(self):
        # 1. Salutations
        salut_regex = r"\b(bonjour|salut|hello|hi|good morning|hey|yo|greetings|morning|bonsoir)\b"
        self.register_rule(
            category=self.SALUTATIONS,
            matcher=lambda text: bool(re.search(salut_regex, text.lower())),
            confidence=1.0,
            recommended_pipeline="Conversation",
            agents_to_trigger=[],
            justification="Le message contient une salutation standard."
        )

        # 2. Conversation générale
        conv_regex = r"\b(merci|thanks|comment vas-tu|comment ça va|comment ca va|how are you|how's it going|ça va|ca va|bien et toi|de rien|s'il te plaît|please)\b"
        self.register_rule(
            category=self.CONVERSATION_GENERALE,
            matcher=lambda text: bool(re.search(conv_regex, text.lower())),
            confidence=0.95,
            recommended_pipeline="Conversation",
            agents_to_trigger=[],
            justification="Le message correspond à un échange de conversation informelle ou de politesse."
        )

        # 3. Commandes système
        sys_regex = r"\b(mémoire|memory|modules|module|journaux|journal|logs|log|système|system|cpu|ram|metrics)\b"
        self.register_rule(
            category=self.COMMANDES_SYSTEME,
            matcher=lambda text: bool(re.search(sys_regex, text.lower())),
            confidence=0.98,
            recommended_pipeline="Commandes système",
            agents_to_trigger=[],
            justification="La requête demande des informations d'état ou de diagnostic système."
        )

        # 4. Gestion des outils
        tool_regex = r"\b(installe|dépendance|configure l'outil|pip|npm|package|dependency|tool|tools)\b"
        self.register_rule(
            category=self.GESTION_OUTILS,
            matcher=lambda text: bool(re.search(tool_regex, text.lower())),
            confidence=0.95,
            recommended_pipeline="Outils",
            agents_to_trigger=[],
            justification="La requête porte sur l'installation de dépendances ou l'utilisation d'outils externes."
        )

        # 5. Sécurité
        sec_regex = r"\b(sûr|sécurité|vulnérabilité|security|safe|vulnerability|exploit|policy check|consent|audit)\b"
        self.register_rule(
            category=self.SECURITE,
            matcher=lambda text: bool(re.search(sec_regex, text.lower())),
            confidence=0.95,
            recommended_pipeline="Développement logiciel",
            agents_to_trigger=["security"],
            justification="La requête concerne une vérification de sécurité ou une analyse de vulnérabilité."
        )

        # 6. Génération de code
        gen_regex = r"\b(génère|écris|générer|écriture|génération)\b.*\b(classe|script|fonction|code|méthode|class|function|method|programme|program)\b|\b(generate|write)\b.*\b(code|class|script|function|method|programme|program)\b"
        self.register_rule(
            category=self.GENERATION_CODE,
            matcher=lambda text: bool(re.search(gen_regex, text.lower())),
            confidence=0.95,
            recommended_pipeline="Développement logiciel",
            agents_to_trigger=["architect", "programmer", "tester", "security", "docs"],
            justification="La requête demande explicitement la création/génération de structures de code."
        )

        # 7. Analyse de code
        anal_regex = r"\b(analyse|recherche|trouve|trouver|analyser|review|analyze|find)\b.*\b(code|bug|bugs|vulnérabilité|vulnérabilités|classe|script|function|fonction)\b"
        self.register_rule(
            category=self.ANALYSE_CODE,
            matcher=lambda text: bool(re.search(anal_regex, text.lower())),
            confidence=0.95,
            recommended_pipeline="Développement logiciel",
            agents_to_trigger=["programmer", "tester", "security"],
            justification="La requête porte sur l'analyse, la relecture de code ou la détection de bugs."
        )

        # 8. Explication de code
        expl_regex = r"\b(explique|explication|comment fonctionne|que fait|explain|how does)\b.*\b(code|script|fonction|function|classe|class|méthode|method)\b"
        self.register_rule(
            category=self.EXPLICATION_CODE,
            matcher=lambda text: bool(re.search(expl_regex, text.lower())),
            confidence=0.90,
            recommended_pipeline="Développement logiciel",
            agents_to_trigger=["programmer", "docs"],
            justification="La requête demande des explications détaillées ou de la documentation sur un extrait de code."
        )

        # 9. Développement logiciel
        dev_regex = r"\b(api|flask|django|serveur|server|web app|base de données|database|développe|développer|implémente|implémenter|build|develop|program|create|implement|integration)\b"
        self.register_rule(
            category=self.DEVELOPPEMENT_LOGICIEL,
            matcher=lambda text: bool(re.search(dev_regex, text.lower())),
            confidence=0.95,
            recommended_pipeline="Développement logiciel",
            agents_to_trigger=["architect", "programmer", "tester", "security", "docs"],
            justification="Le message demande une tâche de développement logiciel complète."
        )

        # 10. Questions techniques
        tech_regex = r"\b(comment fonctionne|explique-moi|c'est quoi|pourquoi|how does|explain|what is|why|kubernetes|docker|network|algorithm)\b"
        self.register_rule(
            category=self.QUESTIONS_TECHNIQUES,
            matcher=lambda text: bool(re.search(tech_regex, text.lower())),
            confidence=0.90,
            recommended_pipeline="Conversation",
            agents_to_trigger=[],
            justification="La requête pose une question conceptuelle ou technique d'ordre général."
        )

        # 11. Recherche d'informations
        search_regex = r"\b(recherche sur le web|cherche des infos|web search|find info|search the internet)\b"
        self.register_rule(
            category=self.RECHERCHE_INFORMATIONS,
            matcher=lambda text: bool(re.search(search_regex, text.lower())),
            confidence=0.90,
            recommended_pipeline="Recherche d'informations",
            agents_to_trigger=[],
            justification="La requête demande explicitement d'effectuer une recherche d'informations."
        )

        # 12. Requêtes complexes
        complex_regex = r"\b(conçois un système complet|orchestre un developpement complexe|concois un systeme complet)\b"
        self.register_rule(
            category=self.REQUETES_COMPLEXES,
            matcher=lambda text: bool(re.search(complex_regex, text.lower())),
            confidence=0.92,
            recommended_pipeline="Requêtes complexes",
            agents_to_trigger=["architect", "programmer", "tester", "security", "docs"],
            justification="La requête exige une orchestration multi-agents avancée pour concevoir un système complet."
        )

    def route(self, prompt: str) -> RoutingDecision:
        """Analyzes a user prompt and returns a structured RoutingDecision."""
        clean_prompt = prompt.strip()
        prompt_lower = clean_prompt.lower()

        # Find the matched rule
        matched_rule = None
        for rule in self._rules:
            if rule.matcher(clean_prompt):
                matched_rule = rule
                break

        # If no rule matched, use fallback rule values
        if matched_rule is None:
            intent = self.INCONNU
            confidence = 0.5
            rule_pipeline = "Conversation"
            agents_to_trigger = []
            justification = "Aucun motif spécifique détecté. Pipeline de conversation par défaut sélectionné."
        else:
            intent = matched_rule.category
            confidence = matched_rule.confidence
            rule_pipeline = matched_rule.recommended_pipeline
            agents_to_trigger = matched_rule.agents_to_trigger
            justification = matched_rule.justification

        # 1. Detect language
        fr_words = ["bonjour", "salut", "comment", "écris", "génère", "analyse", "explique", "sécurité", "qui", "pourquoi", "système", "mémoire", "est", "une", "des", "les", "du", "un", "le", "la", "feuille de route"]
        en_words = ["hello", "hi", "how", "write", "generate", "analyze", "explain", "security", "why", "system", "memory", "is", "a", "an", "the", "of", "to", "it", "roadmap"]
        fr_score = sum(1 for w in fr_words if re.search(r"\b" + re.escape(w) + r"\b", prompt_lower))
        en_score = sum(1 for w in en_words if re.search(r"\b" + re.escape(w) + r"\b", prompt_lower))
        language = "fr" if fr_score >= en_score else "en"

        # 2. Detect domain
        if "python" in prompt_lower:
            domain = "python"
        elif "php" in prompt_lower:
            domain = "php"
        elif "api" in prompt_lower or "rest" in prompt_lower:
            domain = "api"
        elif any(k in prompt_lower for k in ["base de données", "database", "sql", "sqlite", "mysql", "postgres"]):
            domain = "database"
        elif any(k in prompt_lower for k in ["sécurité", "security", "vulnérabilité", "vulnerability", "policy check", "audit"]):
            domain = "security"
        elif any(k in prompt_lower for k in ["mémoire", "memory", "cpu", "ram", "metrics", "modules", "module", "logs", "log", "système", "system"]):
            domain = "system"
        elif any(k in prompt_lower for k in ["outil", "outils", "tool", "tools", "pip", "npm", "package", "dependency"]):
            domain = "tools"
        elif intent in [self.SALUTATIONS, self.CONVERSATION_GENERALE]:
            domain = "conversation"
        elif any(k in prompt_lower for k in ["expliquer", "explique", "explain", "what is", "c'est quoi"]):
            domain = "education"
        else:
            domain = "general"

        # 3. Detect complexity and simple coding status
        simple_coding_keywords = [
            "somme", "addition", "additionne", "calculer la somme", "somme de deux entiers", "hello world", "simple",
            "add two numbers", "sum of two integers", "simple function"
        ]
        is_simple_coding = any(k in prompt_lower for k in simple_coding_keywords)
        is_complex_prompt = any(k in prompt_lower for k in [
            "analyse mon projet", "identifie les problèmes", "corrige-les", "écris les tests", "conçois un système complet",
            "analyse tout mon projet", "corrige les problèmes de sécurité", "orchestre un developpement complexe"
        ])

        if intent in [self.SALUTATIONS, self.CONVERSATION_GENERALE] or prompt_lower in ["bonjour", "salut", "merci", "thanks", "hello", "greetings"]:
            complexity = "trivial"
        elif is_complex_prompt or intent == self.REQUETES_COMPLEXES:
            complexity = "complex"
        elif any(k in prompt_lower for k in ["critique", "critical", "production", "crash"]):
            complexity = "critical"
        elif is_simple_coding:
            complexity = "simple"
        else:
            # Code generation or software development without simple math goes to complex/moderate
            if intent in [self.GENERATION_CODE, self.DEVELOPPEMENT_LOGICIEL, self.ANALYSE_CODE, self.SECURITE]:
                complexity = "complex"
            else:
                complexity = "moderate"

        # 4. Check if we need agents, tools, memory, local model
        requires_tools = any(k in prompt_lower for k in ["pip", "npm", "package", "dependency", "installe", "outil", "tool", "file", "fichier", "analyse mon projet", "tests", "run", "exécute", "execute"])

        if complexity in ["trivial", "simple"]:
            requires_agents = False
            actual_agents_to_trigger = []
        elif is_complex_prompt:
            intent = self.DEVELOPPEMENT_LOGICIEL
            requires_agents = True
            actual_agents_to_trigger = ["architect", "programmer", "tester", "security", "docs"]
        else:
            requires_agents = len(agents_to_trigger) > 0 or complexity in ["complex", "critical"]
            actual_agents_to_trigger = agents_to_trigger

        requires_model = intent in [
            self.SALUTATIONS, self.CONVERSATION_GENERALE, self.GENERATION_CODE, self.ANALYSE_CODE,
            self.EXPLICATION_CODE, self.DEVELOPPEMENT_LOGICIEL, self.QUESTIONS_TECHNIQUES,
            self.REQUETES_COMPLEXES, self.INCONNU, self.SECURITE
        ]

        requires_memory = intent in [
            self.SALUTATIONS, self.CONVERSATION_GENERALE, self.GENERATION_CODE,
            self.EXPLICATION_CODE, self.ANALYSE_CODE, self.DEVELOPPEMENT_LOGICIEL,
            self.REQUETES_COMPLEXES, self.INCONNU, self.SECURITE
        ] or "précédent" in prompt_lower or "previous" in prompt_lower

        sensitive_keywords = ["execute", "run", "exécute", "install", "installe", "supprime", "delete", "format", "write", "modifier", "modify", "crée un fichier", "create file"]
        safety_level = "sensitive" if any(k in prompt_lower for k in sensitive_keywords) else "normal"

        # 5. Pipeline selection
        if complexity == "trivial":
            pipeline = "direct_conversation"
        elif requires_agents:
            pipeline = "agent_task"
        elif intent == self.COMMANDES_SYSTEME:
            pipeline = "system_commands"
        elif intent == self.GESTION_OUTILS:
            pipeline = "tools"
        elif intent in [self.GENERATION_CODE, self.DEVELOPPEMENT_LOGICIEL, self.EXPLICATION_CODE, self.ANALYSE_CODE] and complexity == "simple":
            pipeline = "coding_conversation"
        else:
            pipeline = "conversation"

        return RoutingDecision(
            intent=intent,
            domain=domain,
            complexity=complexity,
            language=language,
            pipeline=pipeline,
            requires_model=requires_model,
            requires_tools=requires_tools,
            requires_agents=requires_agents,
            requires_memory=requires_memory,
            safety_level=safety_level,
            agents_to_trigger=actual_agents_to_trigger,
            justification=justification,
            confidence=confidence
        )

global_intent_router = IntentRouter()
