"""
Custom exceptions for structlogger.

This module defines specific exception types for different error conditions
in the structlogger package, providing clear error messages and better
error handling for users.
"""


class StructLoggerError(Exception):
    """
    Base exception for all structlogger errors.

    This is the parent class for all custom exceptions in the structlogger
    package. It can be used to catch any structlogger-specific error.
    """


class ConfigurationError(StructLoggerError):
    """
    Raised when there's an error in structlogger configuration.

    This exception is raised when invalid configuration parameters are
    provided to configure() or other configuration functions.

    Examples:
        >>> configure(format_type="invalid")
        ConfigurationError: Unsupported format type: invalid

        >>> configure(handler_type="invalid")
        ConfigurationError: Unsupported handler type: invalid
    """


class EnvironmentVariableError(StructLoggerError):
    """
    Raised when a required environment variable is not set.

    This exception is raised when env_fields specifies environment variables
    that are not available in the current environment.

    Examples:
        >>> configure(env_fields={"MISSING_VAR": "missing"})
        EnvironmentVariableError: Required environment variable 'MISSING_VAR' is not set
    """


class FormatterError(StructLoggerError):
    """
    Raised when there's an error in log formatting.

    This exception is raised when the StructFormatter encounters an error
    while formatting log records.
    """


class ContextError(StructLoggerError):
    """
    Raised when there's an error in context management.

    This exception is raised when there are issues with binding or
    managing thread-local context data.
    """
