"""Custom exceptions for core/database module"""

class DatabaseException(Exception):
    """Base exception for core/database module"""
    pass

class DatabaseValidationError(DatabaseException):
    """Raised when module validation fails"""
    pass
