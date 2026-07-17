"""Interfaces and abstract definitions for core/configuration module"""
from abc import ABC, abstractmethod

class IConfigurationService(ABC):
    """Abstract base interface for Configuration service"""

    @abstractmethod
    def get_status(self) -> dict:
        """Retrieve the status of the service"""
        pass
