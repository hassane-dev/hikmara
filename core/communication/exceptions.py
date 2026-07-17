"""Custom exceptions for core/communication module"""

class CommunicationException(Exception):
    """Base exception for core/communication module"""
    pass

class CommunicationValidationError(CommunicationException):
    """Raised when module validation fails"""
    pass
