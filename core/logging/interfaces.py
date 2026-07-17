"""Interfaces and abstract definitions for core/logging module"""
from abc import ABC, abstractmethod

class ILoggingService(ABC):
    """Abstract base interface for Logging service"""

    @abstractmethod
    def get_status(self) -> dict:
        """Retrieve the status of the service"""
        pass
