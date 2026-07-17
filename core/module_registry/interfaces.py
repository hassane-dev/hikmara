"""Interfaces and abstract definitions for core/module_registry module"""
from abc import ABC, abstractmethod

class IModule_registryService(ABC):
    """Abstract base interface for Module_registry service"""

    @abstractmethod
    def get_status(self) -> dict:
        """Retrieve the status of the service"""
        pass
