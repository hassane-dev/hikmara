from typing import List, Dict, Any
from knowledge.service import global_knowledge_base

class KnowledgeRouter:
    def __init__(self):
        pass

    def retrieve_knowledge(self, prompt: str) -> str:
        """Determines if a prompt requires offline document search / RAG and queries the knowledge base."""
        prompt_lower = prompt.lower()

        # Determine keywords to query
        matched_results = []
        for kw in ["python_venv", "venv", "git", "docker", "kubernetes"]:
            if kw in prompt_lower:
                res = global_knowledge_base.query_knowledge(kw)
                if res:
                    matched_results.append(f"Base de connaissances ({kw}) : {res}")

        return "\n\n".join(matched_results) if matched_results else ""

global_knowledge_router = KnowledgeRouter()
