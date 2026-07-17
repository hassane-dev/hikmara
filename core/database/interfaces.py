"""Interfaces and abstract definitions for core/database module"""
from abc import ABC, abstractmethod

class IDatabaseService(ABC):
    """Abstract base interface for Database service"""

    @abstractmethod
    def get_status(self) -> dict:
        """Retrieve the status of the service"""
        pass
