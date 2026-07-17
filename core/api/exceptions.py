"""Custom exceptions for core/api module"""

class ApiException(Exception):
    """Base exception for core/api module"""
    pass

class ApiValidationError(ApiException):
    """Raised when module validation fails"""
    pass
