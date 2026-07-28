from typing import Dict, Any, List
from memory.router import global_memory_router
from knowledge.router import global_knowledge_router
from cognition.context.service import global_context_manager

class KnowledgeRetriever:
    """
    Decoupled retrieval pipeline aggregating memories, documents, vector database,
    and relational knowledge. Connects to SQLite and Vector Store, ranks context, and returns it.
    """
    def __init__(self):
        pass

    def retrieve_context(self, prompt: str, context: Any) -> str:
        # 1. Fetch from Vector Store (Memory Router) using the global_context_manager
        mem_data = global_memory_router.retrieve(prompt, global_context_manager)

        # 2. Fetch from Relational Knowledge Base
        kn_data = global_knowledge_router.retrieve_knowledge(prompt)

        # 3. Simulated Project Documents / Files
        doc_data = ""
        prompt_lower = prompt.lower()
        if any(k in prompt_lower for k in ["readme", "agents.md", "doc"]):
            doc_data = "[Document local] Trouvé doc/AGENTS.md: Hikmara utilise des agents spécialisés (architect, programmer, tester, security, docs) orchestrés par AgentManager."

        # Aggregate & clean
        parts = []
        if mem_data:
            parts.append(f"### Mémoire contextuelle :\n{mem_data}")
        if kn_data:
            parts.append(f"### Connaissances système :\n{kn_data}")
        if doc_data:
            parts.append(f"### Documents associés :\n{doc_data}")

        return "\n\n".join(parts).strip()

global_knowledge_retriever = KnowledgeRetriever()
