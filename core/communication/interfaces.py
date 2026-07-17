"""Interfaces and abstract definitions for core/communication module"""
from abc import ABC, abstractmethod

class ICommunicationService(ABC):
    """Abstract base interface for Communication service"""

    @abstractmethod
    def get_status(self) -> dict:
        """Retrieve the status of the service"""
        pass
