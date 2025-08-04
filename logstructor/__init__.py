"""
structlogger - Cloud-native structured logging for Python

A drop-in replacement for Python's logging module that adds structured logging
capabilities while maintaining 100% compatibility with the standard logging API.
"""

from .config import basic_config, configure, get_logger, reset_configuration
from .context import bind_context, clear_context, get_context, update_context
from .exceptions import (
    ConfigurationError,
    ContextError,
    EnvironmentVariableError,
    FormatterError,
    StructLoggerError,
)
from .formatter import StructFormatter
from .logger import StructLogger

__version__ = "0.2.0"
__all__ = [
    # Core classes
    "StructLogger",
    "StructFormatter",
    # Main functions
    "get_logger",
    "configure",
    "basic_config",
    # Context management
    "bind_context",
    "clear_context",
    "get_context",
    "update_context",
    # Exceptions
    "StructLoggerError",
    "ConfigurationError",
    "EnvironmentVariableError",
    "FormatterError",
    "ContextError",
    # Utilities
    "reset_configuration",
    # Legacy alias
    "getLogger",
]


# Legacy alias for backward compatibility
getLogger = get_logger  # noqa: N816  # noqa: N816
