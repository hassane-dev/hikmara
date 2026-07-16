from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, agent_id, role, permissions):
        self.agent_id = agent_id
        self.role = role
        self.permissions = permissions
        self.history = []

    @abstractmethod
    def execute_task(self, task, context):
        pass
