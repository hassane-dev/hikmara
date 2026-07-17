"""Custom exceptions for core/security module"""

class SecurityException(Exception):
    """Base exception for core/security module"""
    pass

class SecurityValidationError(SecurityException):
    """Raised when module validation fails"""
    pass
