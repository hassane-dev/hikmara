"""Custom exceptions for core/configuration module"""

class ConfigurationException(Exception):
    """Base exception for core/configuration module"""
    pass

class ConfigurationValidationError(ConfigurationException):
    """Raised when module validation fails"""
    pass
