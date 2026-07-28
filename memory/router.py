from typing import List, Dict, Any
from memory.service import global_memory_system

class MemoryRouter:
    def __init__(self):
        pass

    def retrieve(self, prompt: str, context_manager: Any = None) -> str:
        """Determines and retrieves context from appropriate memory sources (RAG, DB, history)."""
        prompt_lower = prompt.lower()
        recalled_snippets = []

        # 1. Query short-term/recent turns from Hybrid Memory
        recent_turns = global_memory_system.conversation_memory[-3:]
        if recent_turns:
            hist_snippet = "Mémoire court-terme (derniers échanges) :\n" + "\n".join([f"- {t['role']}: {t['message']}" for t in recent_turns])
            recalled_snippets.append(hist_snippet)

        # 2. Scan and query SQLite long-term facts database
        for kw in ["nom", "user", "projet", "framework", "database", "langage", "key"]:
            if kw in prompt_lower:
                fact = global_memory_system.retrieve_long_term_fact(kw)
                if fact:
                    recalled_snippets.append(f"Mémoire long-terme ({kw}) : {fact}")

        # 3. Previous generated codes from Session/Context References
        if context_manager:
            ctx = context_manager.get_context()
            last_code = ctx.context_references.get("last_generated_code")
            if last_code:
                recalled_snippets.append(f"Mémoire de travail (Dernier code actif) : Présent")

        return "\n\n".join(recalled_snippets) if recalled_snippets else "Aucune mémoire pertinente trouvée."

global_memory_router = MemoryRouter()
