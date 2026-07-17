"""Interfaces and abstract definitions for core/events module"""
from abc import ABC, abstractmethod

class IEventsService(ABC):
    """Abstract base interface for Events service"""

    @abstractmethod
    def get_status(self) -> dict:
        """Retrieve the status of the service"""
        pass
