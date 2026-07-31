import re
from typing import List, Dict, Any
from cognition.planner.task_analyzer import global_task_complexity_analyzer
from cognition.router.agent_selector import global_agent_selector

class AgentRouter:
    def __init__(self):
        pass

    def decide_agents(self, prompt: str, intent: str, complexity: str) -> Dict[str, Any]:
        """
        Decides if specialized agents need to collaborate and which ones using dynamic selector (Phase 4).
        Abstains from any double decision logic: AgentRouter strictly returns the selection from AgentSelector.
        """
        from cognition.understanding.service import global_language_understanding
        nlu = global_language_understanding.analyze(prompt)

        task_profile = global_task_complexity_analyzer.analyze_task(prompt, nlu)
        selected_agents = global_agent_selector.select_agents(prompt, task_profile)

        return {
            "requires_agents": len(selected_agents) > 0,
            "agents_to_trigger": selected_agents
        }

global_agent_router = AgentRouter()
