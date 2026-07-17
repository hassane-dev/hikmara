"""Custom exceptions for core/tasks module"""

class TasksException(Exception):
    """Base exception for core/tasks module"""
    pass

class TasksValidationError(TasksException):
    """Raised when module validation fails"""
    pass
