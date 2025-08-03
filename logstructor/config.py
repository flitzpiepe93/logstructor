"""
Configuration utilities for structured logging.

This module provides convenient functions to configure structured logging
with sensible defaults, making it easy to get started with minimal setup.
"""

import logging
import os
from typing import Any, Dict, Optional, Union

from .exceptions import ConfigurationError, EnvironmentVariableError
from .formatter import StructFormatter
from .logger import StructLogger

# Track if we've already configured
_configured = False


def _collect_env_fields(
    env_fields: Optional[Dict[str, str]] = None, env_prefix: Optional[str] = None
) -> Dict[str, str]:
    """
    Collect environment variables for inclusion in log context.

    Args:
        env_fields: Dictionary mapping environment variable names to context field names
        env_prefix: Prefix for environment variables to auto-include

    Returns:
        Dictionary of context field names and their values
    """
    env_context = {}

    # Add specific environment fields
    if env_fields:
        for env_var, context_key in env_fields.items():
            value = os.getenv(env_var)
            if value is not None:
                env_context[context_key] = value
            else:
                raise EnvironmentVariableError(f"Required environment variable '{env_var}' is not set")

    # Add environment variables with prefix
    if env_prefix:
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                # Remove prefix and convert to lowercase
                context_key = key[len(env_prefix) :].lower()
                env_context[context_key] = value

    return env_context


def _ensure_configured() -> None:
    """
    Ensure structlogger is configured with sensible defaults.

    This function is called automatically by get_logger() to set up
    structured logging with default settings if configure() hasn't
    been called yet.
    """
    global _configured

    if not _configured:
        # Auto-configure with sensible defaults
        configure()
        _configured = True


def configure(
    level: Union[int, str] = logging.INFO,
    format_type: str = "json",
    timestamp_format: str = "iso",
    extra_fields: Optional[Dict[str, Any]] = None,
    env_fields: Optional[Dict[str, str]] = None,
    env_prefix: Optional[str] = None,
    handler_type: str = "console",
) -> None:
    """
    Configure structured logging with sensible defaults.

    This function sets up structured logging for the entire application
    by configuring the root logger with a StructFormatter and setting
    StructLogger as the default logger class.

    Args:
        level: Logging level (INFO, DEBUG, etc. or logging constants)
        format_type: Output format ("json" is currently the only option)
        timestamp_format: Timestamp format ("iso" or "epoch")
        extra_fields: Static fields to include in every log entry
        env_fields: Dictionary mapping environment variable names to context field names
        env_prefix: Prefix for environment variables to auto-include (e.g. "APP_")
        handler_type: Handler type ("console" is currently the only option)

    Examples:
        Basic setup:
        >>> configure()
        >>> logger = structlogger.getLogger(__name__)
        >>> logger.info("Hello world")

        Custom level and fields:
        >>> configure(
        ...     level="DEBUG",
        ...     extra_fields={"service": "my-app", "version": "1.0.0"}
        ... )

        Production setup:
        >>> configure(
        ...     level=logging.WARNING,
        ...     extra_fields={"environment": "production", "service": "api"}
        ... )

        With environment variables:
        >>> configure(env_fields={"SERVICE_NAME": "service", "VERSION": "version", "ENVIRONMENT": "env"})
        >>> # Maps SERVICE_NAME -> service, VERSION -> version, ENVIRONMENT -> env in context

        With environment prefix:
        >>> configure(env_prefix="APP_")
        >>> # Includes all APP_* environment variables in context

        Combined approach:
        >>> configure(
        ...     env_prefix="APP_",
        ...     env_fields={"SERVICE_NAME": "service"},
        ...     extra_fields={"component": "api"}
        ... )
    """
    global _configured

    # Set StructLogger as the default logger class
    logging.setLoggerClass(StructLogger)

    # Get root logger and clear existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # Set logging level
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    root_logger.setLevel(level)

    # Create handler
    if handler_type == "console":
        handler = logging.StreamHandler()
    else:
        raise ConfigurationError(f"Unsupported handler type: {handler_type}")

    # Collect environment variables
    env_context = _collect_env_fields(env_fields, env_prefix)

    # Merge extra_fields with environment context
    combined_extra_fields = {}
    if extra_fields:
        combined_extra_fields.update(extra_fields)
    combined_extra_fields.update(env_context)

    # Create formatter
    if format_type == "json":
        formatter = StructFormatter(
            timestamp_format=timestamp_format,
            extra_fields=combined_extra_fields if combined_extra_fields else None,
        )
    else:
        raise ConfigurationError(f"Unsupported format type: {format_type}")

    # Set up handler and add to root logger
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Mark as configured
    _configured = True


def basic_config(**kwargs) -> None:
    """
    Basic configuration for structured logging.

    This is an alias for configure() that mimics the standard logging.basicConfig()
    function name for familiarity.

    Args:
        **kwargs: Same arguments as configure()

    Examples:
        >>> basic_config(level="DEBUG")
        >>> logger = structlogger.getLogger(__name__)
        >>> logger.info("Configured with basic_config")
    """
    configure(**kwargs)


def get_logger(name: Optional[str] = None) -> StructLogger:
    """
    Get a structured logger instance.

    This function returns a StructLogger instance, which provides structured
    logging capabilities while maintaining full compatibility with the
    standard logging API.

    Args:
        name: Logger name (typically __name__ or None for root logger)

    Returns:
        StructLogger instance

    Examples:
        Module logger:
        >>> logger = get_logger(__name__)
        >>> logger.info("Module-specific logger")

        Root logger:
        >>> logger = get_logger()
        >>> logger.info("Root logger")

        Named logger:
        >>> logger = get_logger("my_component")
        >>> logger.info("Component logger")
    """
    # Auto-configure with defaults if not already configured
    _ensure_configured()

    return logging.getLogger(name)  # type: ignore[return-value]


def reset_configuration() -> None:
    """
    Reset logging configuration to defaults.

    This function clears all handlers from the root logger and resets
    the logger class to the standard logging.Logger. Useful for testing
    or when you need to reconfigure logging completely.

    Examples:
        >>> configure(level="DEBUG")
        >>> # ... use structured logging ...
        >>> reset_configuration()
        >>> # Back to standard logging
    """
    # Reset logger class to standard
    logging.setLoggerClass(logging.Logger)

    # Clear root logger handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # Reset level to default
    root_logger.setLevel(logging.WARNING)

    # Mark as not configured
    global _configured
    _configured = False
