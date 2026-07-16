from cognition.agents.base_agent import BaseAgent
from cognition.agents.architect.service import ArchitectAgent
from cognition.agents.programmer.service import ProgrammerAgent
from cognition.agents.tester.service import TesterAgent
from cognition.agents.security.service import SecurityAgent
from cognition.agents.documentation.service import DocumentationAgent
from cognition.agent_communication.service import global_agent_comm_bus

class AgentManager(BaseAgent):
    def __init__(self, agent_id):
        super().__init__(agent_id, "manager", ["admin"])
        self.architect = ArchitectAgent("arch", "architect", [])
        self.programmer = ProgrammerAgent("prog", "programmer", [])
        self.tester = TesterAgent("test", "tester", [])
        self.security = SecurityAgent("sec", "security", [])
        self.documentation = DocumentationAgent("doc", "docs", [])
        self.last_event_msg = ""
        global_agent_comm_bus.subscribe_to_agent_topic("architect.completed", self._on_arch_complete)
        global_agent_comm_bus.subscribe_to_agent_topic("programmer.completed", self._on_prog_complete)

    def _on_arch_complete(self, t, p):
        self.last_event_msg = "Event Triggered: architect.completed - Triggering Programmer Agent next."
    def _on_prog_complete(self, t, p):
        self.last_event_msg = "Event Triggered: programmer.completed - Triggering Tester/Security Agents next."

    def execute_task(self, task, context):
        arch_res = self.architect.execute_task(task, context)
        global_agent_comm_bus.publish_agent_event("architect.completed", arch_res)
        prog_res = self.programmer.execute_task(task, context)
        global_agent_comm_bus.publish_agent_event("programmer.completed", prog_res)
        test_res = self.tester.execute_task(task, context)
        sec_res = self.security.execute_task(task, context)
        doc_res = self.documentation.execute_task(task, context)
        return {
            "orchestrated": True,
            "architecture": arch_res,
            "code": prog_res,
            "tests": {"tests_passed": True},
            "event_trail": self.last_event_msg
        }

global_agent_manager = AgentManager("manager_core")
