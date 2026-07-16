from cognition.agents.base_agent import BaseAgent

class DocumentationAgent(BaseAgent):
    def execute_task(self, task, context):
        return {"status": "success", "agent": self.agent_id, "readme": "# Done"}
