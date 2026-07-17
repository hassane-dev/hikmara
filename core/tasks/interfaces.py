"""Interfaces and abstract definitions for core/tasks module"""
from abc import ABC, abstractmethod

class ITasksService(ABC):
    """Abstract base interface for Tasks service"""

    @abstractmethod
    def get_status(self) -> dict:
        """Retrieve the status of the service"""
        pass
