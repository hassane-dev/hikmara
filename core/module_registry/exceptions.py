"""Custom exceptions for core/module_registry module"""

class Module_registryException(Exception):
    """Base exception for core/module_registry module"""
    pass

class Module_registryValidationError(Module_registryException):
    """Raised when module validation fails"""
    pass
