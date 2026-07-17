"""Interfaces and abstract definitions for core/api module"""
from abc import ABC, abstractmethod

class IApiService(ABC):
    """Abstract base interface for Api service"""

    @abstractmethod
    def get_status(self) -> dict:
        """Retrieve the status of the service"""
        pass
