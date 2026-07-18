import re
from typing import List, Callable, Dict, Any
from cognition.router.models import IntentResult

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

        # 2. Conversation générale (make sure 'comment vas tu' and variations are perfectly captured)
        conv_regex = r"\b(merci|thanks|comment vas tu|comment vas-tu|comment ça va|comment ca va|how are you|how's it going|ça va|ca va|bien et toi|de rien|s'il te plaît|please)\b"
        self.register_rule(
            category=self.CONVERSATION_GENERALE,
            matcher=lambda text: bool(re.search(conv_regex, text.lower())) or "comment vas" in text.lower(),
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

        # 6. Ambiguous "code" query (route to Conversation to ask for clarification without launching agents)
        self.register_rule(
            category=self.GENERATION_CODE,
            matcher=lambda text: text.strip().lower() in ["code", "le code", "du code"],
            confidence=0.85,
            recommended_pipeline="Conversation",
            agents_to_trigger=[],
            justification="La requête contient uniquement le mot 'code' et est ambiguë. Clarification requise."
        )

        # 7. Planification de projet / Feuille de route
        roadmap_regex = r"\b(feuille de route|roadmap|planification|planning|projet web|conception de projet|gérer un projet|projet de site)\b"
        self.register_rule(
            category=self.QUESTIONS_TECHNIQUES,
            matcher=lambda text: bool(re.search(roadmap_regex, text.lower())),
            confidence=0.95,
            recommended_pipeline="Conversation",
            agents_to_trigger=[],
            justification="La requête concerne une demande de planification de projet ou de conseil technique."
        )

        # 8. PHP script / scripting languages pattern
        scripting_regex = r"\b(php|python|javascript|js|flask|django|api|html|css|c\+\+|java)\b"
        self.register_rule(
            category=self.GENERATION_CODE,
            matcher=lambda text: bool(re.search(scripting_regex, text.lower())) and any(v in text.lower() for v in ["écris", "génère", "crée", "code", "script", "somme", "entiers", "write", "generate"]),
            confidence=0.97,
            recommended_pipeline="Développement logiciel",
            agents_to_trigger=["architect", "programmer", "tester", "security", "docs"],
            justification="La requête demande explicitement la création/génération de structures de code avec un langage cible."
        )

        # 9. Génération de code general
        gen_regex = r"\b(génère|écris|générer|écriture|génération)\b.*\b(classe|script|fonction|code|méthode|class|function|method)\b|\b(generate|write)\b.*\b(code|class|script|function|method)\b"
        self.register_rule(
            category=self.GENERATION_CODE,
            matcher=lambda text: bool(re.search(gen_regex, text.lower())),
            confidence=0.95,
            recommended_pipeline="Développement logiciel",
            agents_to_trigger=["architect", "programmer", "tester", "security", "docs"],
            justification="La requête demande la génération de code."
        )

        # 10. Analyse de code
        anal_regex = r"\b(analyse|recherche|trouve|trouver|analyser|review|analyze|find)\b.*\b(code|bug|bugs|vulnérabilité|vulnérabilités|classe|script|function|fonction)\b"
        self.register_rule(
            category=self.ANALYSE_CODE,
            matcher=lambda text: bool(re.search(anal_regex, text.lower())),
            confidence=0.95,
            recommended_pipeline="Développement logiciel",
            agents_to_trigger=["programmer", "tester", "security"],
            justification="La requête porte sur l'analyse, la relecture de code ou la détection de bugs."
        )

        # 11. Explication de code
        expl_regex = r"\b(explique|explication|comment fonctionne|que fait|explain|how does)\b.*\b(code|script|fonction|function|classe|class|méthode|method)\b"
        self.register_rule(
            category=self.EXPLICATION_CODE,
            matcher=lambda text: bool(re.search(expl_regex, text.lower())),
            confidence=0.90,
            recommended_pipeline="Développement logiciel",
            agents_to_trigger=["programmer", "docs"],
            justification="La requête demande des explications détaillées ou de la documentation sur un extrait de code."
        )

        # 12. Développement logiciel
        dev_regex = r"\b(api|flask|django|serveur|server|web app|base de données|database|développe|développer|implémente|implémenter|build|develop|program|create|implement|integration)\b"
        self.register_rule(
            category=self.DEVELOPPEMENT_LOGICIEL,
            matcher=lambda text: bool(re.search(dev_regex, text.lower())),
            confidence=0.95,
            recommended_pipeline="Développement logiciel",
            agents_to_trigger=["architect", "programmer", "tester", "security", "docs"],
            justification="Le message demande une tâche de développement logiciel complète."
        )

        # 13. Questions techniques
        tech_regex = r"\b(comment fonctionne|explique-moi|c'est quoi|pourquoi|how does|explain|what is|why|kubernetes|docker|network|algorithm)\b"
        self.register_rule(
            category=self.QUESTIONS_TECHNIQUES,
            matcher=lambda text: bool(re.search(tech_regex, text.lower())),
            confidence=0.90,
            recommended_pipeline="Conversation",
            agents_to_trigger=[],
            justification="La requête pose une question conceptuelle ou technique d'ordre général."
        )

        # 14. Recherche d'informations
        search_regex = r"\b(recherche sur le web|cherche des infos|web search|find info|search the internet)\b"
        self.register_rule(
            category=self.RECHERCHE_INFORMATIONS,
            matcher=lambda text: bool(re.search(search_regex, text.lower())),
            confidence=0.90,
            recommended_pipeline="Recherche d'informations",
            agents_to_trigger=[],
            justification="La requête demande explicitement d'effectuer une recherche d'informations."
        )

        # 15. Requêtes complexes
        complex_regex = r"\b(conçois un système complet|orchestre un developpement complexe|concois un systeme complet)\b"
        self.register_rule(
            category=self.REQUETES_COMPLEXES,
            matcher=lambda text: bool(re.search(complex_regex, text.lower())),
            confidence=0.92,
            recommended_pipeline="Requêtes complexes",
            agents_to_trigger=["architect", "programmer", "tester", "security", "docs"],
            justification="La requête exige une orchestration multi-agents avancée pour concevoir un système complet."
        )

    def route(self, prompt: str) -> IntentResult:
        """Analyzes a user prompt and returns a structured IntentResult."""
        clean_prompt = prompt.strip()
        # Evaluate registered rules
        for rule in self._rules:
            if rule.matcher(clean_prompt):
                return IntentResult(
                    category=rule.category,
                    confidence=rule.confidence,
                    recommended_pipeline=rule.recommended_pipeline,
                    agents_to_trigger=rule.agents_to_trigger,
                    justification=rule.justification
                )

        # Fallback for unknown / general queries
        return IntentResult(
            category=self.INCONNU,
            confidence=0.5,
            recommended_pipeline="Conversation",
            agents_to_trigger=[],
            justification="Aucun motif spécifique détecté. Pipeline de conversation par défaut sélectionné."
        )

global_intent_router = IntentRouter()
