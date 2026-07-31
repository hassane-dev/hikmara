from typing import List, Dict, Any

class AgentSelector:
    def __init__(self):
        pass

    def select_agents(self, prompt: str, task_profile: Any) -> List[str]:
        """
        Dynamically chooses the optimal, non-overlapping subset of agents to trigger.
        Complies with strict selection rules (no full-cascades by default, specialized security filters).
        """
        prompt_lower = prompt.lower().strip()
        agents = []

        # 1. Base agents from task analyzer profile
        for agent in task_profile.recommended_agents:
            if agent not in agents:
                agents.append(agent)

        # 2. Strict constraint rules application
        # RÈGLE 2: Tester uniquement si demandé ou si base de données complexe est modifiée
        if "tester" in agents:
            is_test_explicit = any(k in prompt_lower for k in ["test", "valide", "vérifie", "check", "assert"])
            is_complex_dev = len(agents) >= 4 or "refactor" in prompt_lower
            if not (is_test_explicit or is_complex_dev):
                agents.remove("tester")

        # RÈGLE 3: Security uniquement sur audit, auth, crypto, réseau, ou données hautement sensibles
        if "security" in agents:
            is_security_needed = any(k in prompt_lower for k in [
                "sécurité", "security", "audit", "auth", "login", "connexion", "mdp", "password",
                "crypt", "réseau", "network", "port", "sensible", "vulnerab"
            ])
            if not is_security_needed:
                agents.remove("security")

        # Guard-rail: Protect against user requesting to "run all agents" blindly
        if any(k in prompt_lower for k in ["lance tous les agents", "exécute tout", "run all tasks"]):
            # Reset selection to prompt user with a clean option
            return []

        return agents

global_agent_selector = AgentSelector()
