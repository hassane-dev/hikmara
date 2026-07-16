from cognition.agents.base_agent import BaseAgent

class SecurityAgent(BaseAgent):
    def execute_task(self, task, context):
        return {"status": "success", "agent": self.agent_id, "secure_pass": True}
