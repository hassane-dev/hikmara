from typing import List, Dict, Any
from memory.service import global_memory_system

class MemoryRetriever:
    def __init__(self):
        pass

    def retrieve_context(self, prompt: str) -> str:
        """Retrieves relevant facts from short-term memory or databases to enrich prompts."""
        prompt_lower = prompt.lower()
        context_snippets = []

        # Scan for potential keywords to recall long-term facts
        keywords = ["nom", "user", "projet", "framework", "database", "langage"]
        for kw in keywords:
            if kw in prompt_lower:
                fact = global_memory_system.retrieve_long_term_fact(kw)
                if fact:
                    context_snippets.append(f"Fait connu ({kw}) : {fact}")

        # Sync/get last conversation messages as memory context
        turns = global_memory_system.conversation_memory[-4:] # Last 4 turns
        if turns:
            history_str = "Historique récent :\n" + "\n".join([f"- {t['role']}: {t['message']}" for t in turns])
            context_snippets.append(history_str)

        return "\n\n".join(context_snippets) if context_snippets else ""

global_memory_retriever = MemoryRetriever()
