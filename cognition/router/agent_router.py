import re
from typing import List, Dict, Any

class AgentRouter:
    def __init__(self):
        pass

    def decide_agents(self, prompt: str, intent: str, complexity: str) -> Dict[str, Any]:
        """Decides if specialized agents need to collaborate and which ones."""
        prompt_lower = prompt.lower()
        requires_agents = False
        agents_to_trigger = []

        is_complex = complexity == "complex"
        # Determine if it's a high-complexity structural development task
        is_structural_dev = intent in ["Développement logiciel", "Génération de code"] and complexity == "moderate"

        if is_complex or is_structural_dev:
            requires_agents = True
            agents_to_trigger = ["architect", "programmer", "tester", "security", "docs"]
        elif intent == "Sécurité":
            requires_agents = True
            agents_to_trigger = ["security"]

        return {
            "requires_agents": requires_agents,
            "agents_to_trigger": agents_to_trigger
        }

global_agent_router = AgentRouter()
