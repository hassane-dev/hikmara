"""Custom exceptions for core/system module"""

class SystemException(Exception):
    """Base exception for core/system module"""
    pass

class SystemValidationError(SystemException):
    """Raised when module validation fails"""
    pass
