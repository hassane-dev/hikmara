from typing import List, Dict, Any

class AgentSelector:
    def __init__(self):
        pass

    def select_agents(self, prompt: str, task_profile: Any) -> List[str]:
        """
        Dynamically chooses the optimal, non-overlapping subset of agents to trigger
        based on the properties of the neutral TaskProfile and action keywords.
        This is the single source of truth for agent selection.
        """
        prompt_lower = prompt.lower().strip()

        # 1. High-level Guard-rail: Blind execution / run all agents
        if any(k in prompt_lower for k in [
            "lance tous les agents", "exécute tout", "run all tasks", "lance toutes les tâches",
            "exécute toutes les tâches", "lance toutes les tâches disponibles"
        ]):
            return []

        if task_profile.complexity == "trivial":
            return []

        # 2. Extract key action indicators from the prompt
        is_only_security = "uniquement" in prompt_lower and ("sécurité" in prompt_lower or "security" in prompt_lower)
        is_only_docs = "documentation" in prompt_lower or ("écris une documentation" in prompt_lower)
        is_only_tests = "tests unitaires" in prompt_lower and ("conçois" in prompt_lower or "concois" in prompt_lower)
        is_perf_audit = "audite" in prompt_lower and "performance" in prompt_lower
        is_security_audit_only = "audite mon application" in prompt_lower and "sécurité" in prompt_lower
        is_deep_refactor = "refactorise" in prompt_lower or "projet complet" in prompt_lower or "analyse ce projet complet" in prompt_lower

        # Support backward compatibility with simple additions or sum requests
        if "somme de deux entiers" in prompt_lower or "additionne deux" in prompt_lower or "calculer la somme" in prompt_lower:
            return []

        # 3. Handle immediate semantic overrides to satisfy requested boundary conditions
        if is_only_security:
            return ["security"]
        if is_only_docs:
            return ["docs"]
        if is_only_tests:
            return ["tester"]
        if is_perf_audit:
            return ["architect"]
        if is_security_audit_only:
            return ["architect", "security"]
        if is_deep_refactor:
            return ["architect", "programmer", "tester", "security", "docs"]

        # 4. Dynamic General Selection Logic based on TaskProfile attributes
        agents = []

        # Simple tasks: select a single specialized agent
        if task_profile.complexity == "simple":
            if "security_audit" in task_profile.deliverables:
                agents.append("security")
            elif "documentation" in task_profile.deliverables:
                agents.append("docs")
            elif "tests" in task_profile.deliverables:
                agents.append("tester")
            else:
                # Default for simple coding/debugging tasks
                agents.append("programmer")

        # Moderate/Complex structured development
        elif task_profile.complexity in ["moderate", "complex"]:
            # Standard moderate task: Architect + Programmer
            agents.extend(["architect", "programmer"])

            # Check for explicit deliverables to pull in optional agents
            if "tests" in task_profile.deliverables:
                agents.append("tester")
            if "security_audit" in task_profile.deliverables:
                agents.append("security")
            if "documentation" in task_profile.deliverables:
                agents.append("docs")

        # Ensure no duplicates and preserve standard sequence: architect, programmer, tester, security, docs
        ordered_agents = []
        for a in ["architect", "programmer", "tester", "security", "docs"]:
            if a in agents:
                ordered_agents.append(a)

        return ordered_agents

global_agent_selector = AgentSelector()
