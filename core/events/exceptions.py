"""Custom exceptions for core/events module"""

class EventsException(Exception):
    """Base exception for core/events module"""
    pass

class EventsValidationError(EventsException):
    """Raised when module validation fails"""
    pass
