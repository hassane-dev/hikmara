from cognition.agents.base_agent import BaseAgent

class ProgrammerAgent(BaseAgent):
    def execute_task(self, task, context):
        return {"status": "success", "agent": self.agent_id, "code": "import sys"}
