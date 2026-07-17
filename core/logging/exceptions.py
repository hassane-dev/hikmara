"""Custom exceptions for core/logging module"""

class LoggingException(Exception):
    """Base exception for core/logging module"""
    pass

class LoggingValidationError(LoggingException):
    """Raised when module validation fails"""
    pass
