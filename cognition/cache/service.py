from typing import Dict, Optional

class ResponseCache:
    """
    Offline response cache for trivial questions and answers (e.g., greetings, politeness)
    to avoid redundant local model inference and improve UI latency.
    """
    def __init__(self):
        self._cache: Dict[str, str] = {}
        self._prefill_trivial_cache()

    def _prefill_trivial_cache(self):
        # Cache simple questions/answers (lowered keys)
        self._cache["bonjour"] = "Bonjour ! Comment puis-je vous aider aujourd'hui ?"
        self._cache["good morning"] = "Good morning! How can I help you today?"
        self._cache["hello"] = "Hello! How can I assist you today?"
        self._cache["comment te sens-tu ?"] = "En tant qu'assistant Hikmara AI local, je me sens parfaitement bien et opérationnel à 100% hors-ligne ! Et vous ?"
        self._cache["comment te sens-tu"] = "En tant qu'assistant Hikmara AI local, je me sens parfaitement bien et opérationnel à 100% hors-ligne ! Et vous ?"
        self._cache["comment t'appelles-tu ?"] = "Je m'appelle Hikmara AI, votre assistant personnel universel fonctionnant localement."
        self._cache["comment t'appelles-tu"] = "Je m'appelle Hikmara AI, votre assistant personnel universel fonctionnant localement."
        self._cache["qui es-tu ?"] = "Je suis Hikmara AI, un assistant d'intelligence locale universel, hautement sécurisé et fonctionnant 100% hors-ligne."
        self._cache["qui es-tu"] = "Je suis Hikmara AI, un assistant d'intelligence locale universel, hautement sécurisé et fonctionnant 100% hors-ligne."

    def get(self, prompt: str) -> Optional[str]:
        clean_key = prompt.strip().lower().rstrip("?.!")
        return self._cache.get(clean_key)

    def set(self, prompt: str, response: str):
        clean_key = prompt.strip().lower().rstrip("?.!")
        # Only cache relatively short queries to avoid bloat
        if len(clean_key) < 100:
            self._cache[clean_key] = response

    def clear(self):
        self._cache.clear()
        self._prefill_trivial_cache()

global_response_cache = ResponseCache()
