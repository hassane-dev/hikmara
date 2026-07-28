import re
from typing import Dict, Any, List
from cognition.nlu.models import LanguageUnderstandingResult

class LanguageUnderstandingService:
    def __init__(self):
        # Compile intent regular expressions
        self._intents_patterns = {
            "greeting": r"\b(bonjour|salut|hello|hi|good morning|greetings|morning|hey|yo|bonsoir)\b",
            "general_conversation": r"\b(comment vas-tu|comment ça va|comment ca va|how are you|how's it going|merci|thanks|thank you|de rien|s'il te plaît|please|qui es-tu|who are you)\b",
            "code_conversion": r"\b(convertis|transforme|réécris|convert|rewrite|translate|traduis)\b",
            "code_modification": r"\b(ajoute|modifie|améliore|change|connecte|add|modify|improve|update|change|connect|intègre|integre)\b",
            "code_generation": r"\b(génère|écris|générer|écriture|génération|crée|cree|fais-moi|fais moi|développe|developpe|generate|write|create|build|make me|program|programme|script|code|fonction|function|classe|class)\b",
            "explanation": r"\b(explique|explication|comment fonctionne|que fait|explain|how does|why|pourquoi|c'est quoi|what is)\b",
            "system": r"\b(mémoire|memory|modules|module|journaux|journal|logs|log|système|system|cpu|ram|metrics)\b",
            "tools": r"\b(installe|dépendance|configure l'outil|pip|npm|package|dependency|tool|tools|crée un fichier|create file|lis ce fichier|read file|analyse ce dossier|analyze folder|exécute ce script|run script|delete file|supprime fichier)\b"
        }

        # Domain keywords
        self._domain_keywords = {
            "python": [r"\bpython\b", r"\bpy\b"],
            "php": [r"\bphp\b"],
            "javascript": [r"\bjavascript\b", r"\bjs\b", r"\bnode\b"],
            "java": [r"\bjava\b"],
            "cpp": [r"\bc\+\+\b", r"\bcpp\b"],
            "c": [r"\bc\b"],
            "sql": [r"\bsql\b"],
            "html": [r"\bhtml\b"],
            "css": [r"\bcss\b"],
            "database": [r"\b(database|base de données|base de donnees|sqlite|postgres|mysql|oracle|nosql)\b"],
            "system": [r"\b(cpu|ram|disk|disque|mémoire|memory|system|système)\b"],
            "tools": [r"\b(pip|npm|dependency|dependance|file|fichier|script|execute|run|exécute)\b"]
        }

    def analyze(self, text: str) -> LanguageUnderstandingResult:
        """Analyzes a user message to extract language, intent, domain, entities, and confidence."""
        clean_text = text.strip()
        text_lower = clean_text.lower()

        # 1. Detect language
        fr_score = len(re.findall(r"\b(bonjour|salut|comment|écris|génère|analyse|explique|sécurité|qui|pourquoi|système|mémoire|est|une|des|les|du|un|le|la|fais-moi|ajoute|modifie|somme|entiers|nombres)\b", text_lower))
        en_score = len(re.findall(r"\b(hello|hi|how|write|generate|analyze|explain|security|why|system|memory|is|a|an|the|of|to|it|make-me|add|modify|sum|integers|numbers)\b", text_lower))
        language = "fr" if fr_score >= en_score else "en"

        # 2. Detect intent based on pattern matching with priority
        detected_intent = "unknown"
        matched_pattern = None

        # Check order of intents to avoid wrong matches (e.g., code_conversion/code_modification take precedence over code_generation)
        intent_priority = ["greeting", "general_conversation", "code_conversion", "code_modification", "explanation", "system", "tools", "code_generation"]

        for intent_name in intent_priority:
            pattern = self._intents_patterns[intent_name]
            if re.search(pattern, text_lower):
                detected_intent = intent_name
                matched_pattern = pattern
                break

        # 3. Detect domain
        detected_domain = "general"
        for domain_name, patterns in self._domain_keywords.items():
            if any(re.search(pat, text_lower) for pat in patterns):
                detected_domain = domain_name
                break

        if detected_intent in ["greeting", "general_conversation"] and detected_domain == "general":
            detected_domain = "conversation"

        # 4. Extract entities
        entities = {}
        if any(w in text_lower for w in ["somme", "addition", "additionne", "add", "sum"]):
            entities["operation"] = "addition"
        if any(w in text_lower for w in ["entier", "entiers", "integer", "integers"]):
            entities["data_type"] = "integer"
        if "sqlite" in text_lower or "base de données" in text_lower or "database" in text_lower:
            entities["database_type"] = "sqlite" if "sqlite" in text_lower else "sql"
        if any(w in text_lower for w in ["interface graphique", "gui", "graphique", "visuel", "pyqt", "pyqt6"]):
            entities["interface_type"] = "pyqt6"

        # 5. Check follow up or contextual references
        is_follow_up = any(w in text_lower for w in ["précédent", "previous", "ajoute", "add", "modifie", "modify", "encore", "plus", "plus tard", "change", "convertis", "transforme", "réécris"])
        references_previous_context = any(w in text_lower for w in ["précédent", "previous", "programme d'avant", "code d'avant", "dernier", "last", "le programme", "ce code"])

        # 6. Assess security risk
        risks_security = "normal"
        sensitive_keywords = ["execute", "run", "exécute", "install", "installe", "supprime", "delete", "format", "write", "modifier", "modify", "crée un fichier", "create file"]
        if any(k in text_lower for k in sensitive_keywords):
            risks_security = "sensitive"

        # 7. Calculate confidence
        confidence = 0.40
        if detected_intent != "unknown":
            confidence = 0.95
            words = text_lower.split()
            if len(words) <= 2 and detected_intent not in ["greeting", "system", "general_conversation"]:
                confidence = 0.75
        else:
            if len(text_lower) > 30:
                confidence = 0.50

        # Determine needs_memory and needs_tools
        needs_memory = is_follow_up or references_previous_context or detected_intent in ["general_conversation", "code_modification", "code_conversion"]
        needs_tools = detected_intent == "tools" or risks_security == "sensitive"

        return LanguageUnderstandingResult(
            text=clean_text,
            language=language,
            intent=detected_intent,
            domain=detected_domain,
            entities=entities,
            confidence=confidence,
            is_follow_up=is_follow_up,
            references_previous_context=references_previous_context,
            needs_memory=needs_memory,
            needs_tools=needs_tools,
            risks_security=risks_security
        )

global_language_understanding = LanguageUnderstandingService()
