from abc import ABC, abstractmethod

class BaseTool(ABC):
    def __init__(self, name, description, permissions_required):
        self.name = name
        self.description = description
        self.permissions_required = permissions_required

    @abstractmethod
    def execute(self, params):
        pass
