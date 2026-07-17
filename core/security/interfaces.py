"""Interfaces and abstract definitions for core/security module"""
from abc import ABC, abstractmethod

class ISecurityService(ABC):
    """Abstract base interface for Security service"""

    @abstractmethod
    def get_status(self) -> dict:
        """Retrieve the status of the service"""
        pass
