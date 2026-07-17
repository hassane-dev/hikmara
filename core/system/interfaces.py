"""Interfaces and abstract definitions for core/system module"""
from abc import ABC, abstractmethod

class ISystemService(ABC):
    """Abstract base interface for System service"""

    @abstractmethod
    def get_status(self) -> dict:
        """Retrieve the status of the service"""
        pass
