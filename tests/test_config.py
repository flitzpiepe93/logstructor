"""
Tests for structlogger.config module.

Tests configuration functions and auto-configuration behavior.
"""

import logging
import os
from unittest.mock import patch

import pytest

from logstructor.config import _collect_env_fields, basic_config, configure, get_logger, reset_configuration
from logstructor.exceptions import ConfigurationError, EnvironmentVariableError
from logstructor.formatter import StructFormatter
from logstructor.logger import StructLogger


@pytest.fixture(autouse=True)
def reset_config():
    """Reset configuration before and after each test."""
    reset_configuration()
    yield
    reset_configuration()


def test_configure_basic():
    """Test basic configuration."""
    configure(level="DEBUG")

    root_logger = logging.getLogger()

    # Should have StructLogger as default class
    assert logging.getLoggerClass() == StructLogger

    # Should have correct level
    assert root_logger.level == logging.DEBUG

    # Should have handler with StructFormatter
    assert len(root_logger.handlers) == 1
    handler = root_logger.handlers[0]
    assert isinstance(handler.formatter, StructFormatter)


def test_configure_with_extra_fields():
    """Test configuration with static extra fields."""
    extra_fields = {"service": "test-service", "version": "1.0.0"}
    configure(extra_fields=extra_fields)

    root_logger = logging.getLogger()
    handler = root_logger.handlers[0]
    formatter = handler.formatter

    assert formatter.extra_fields == extra_fields


@pytest.mark.parametrize(
    "invalid_type,error_message",
    [
        ("invalid_format", "Unsupported format type: invalid_format"),
        ("xml", "Unsupported format type: xml"),
    ],
)
def test_configure_invalid_format_type(invalid_type, error_message):
    """Test configuration with invalid format type."""
    with pytest.raises(ConfigurationError, match=error_message):
        configure(format_type=invalid_type)


@pytest.mark.parametrize(
    "invalid_handler,error_message",
    [
        ("invalid_handler", "Unsupported handler type: invalid_handler"),
        ("file", "Unsupported handler type: file"),
    ],
)
def test_configure_invalid_handler_type(invalid_handler, error_message):
    """Test configuration with invalid handler type."""
    with pytest.raises(ConfigurationError, match=error_message):
        configure(handler_type=invalid_handler)


def test_basic_config_alias():
    """Test that basic_config is an alias for configure."""
    basic_config(level="WARNING")

    root_logger = logging.getLogger()
    assert root_logger.level == logging.WARNING


def test_get_logger_auto_configures():
    """Test that get_logger auto-configures with defaults."""
    # Should not be configured initially
    assert logging.getLoggerClass() == logging.Logger

    logger = get_logger("test")

    # Should auto-configure
    assert logging.getLoggerClass() == StructLogger
    assert isinstance(logger, StructLogger)

    # Should have default configuration
    root_logger = logging.getLogger()
    assert root_logger.level == logging.INFO  # Default level
    assert len(root_logger.handlers) == 1


def test_get_logger_doesnt_reconfigure():
    """Test that get_logger doesn't reconfigure if already configured."""
    # Configure explicitly first
    configure(level="DEBUG")
    original_level = logging.getLogger().level

    # Get logger shouldn't change configuration
    get_logger("test")

    assert logging.getLogger().level == original_level


def test_reset_configuration():
    """Test configuration reset."""
    # Configure first
    configure(level="DEBUG")
    assert logging.getLoggerClass() == StructLogger

    # Reset
    reset_configuration()

    # Should be back to defaults
    assert logging.getLoggerClass() == logging.Logger
    root_logger = logging.getLogger()
    assert len(root_logger.handlers) == 0
    assert root_logger.level == logging.WARNING


def test_collect_env_fields_with_dict():
    """Test _collect_env_fields with env_fields dict."""
    with patch.dict(os.environ, {"TEST_VAR": "test_value", "ANOTHER_VAR": "another_value"}):
        env_fields = {"TEST_VAR": "test", "ANOTHER_VAR": "another"}
        result = _collect_env_fields(env_fields=env_fields)

        expected = {"test": "test_value", "another": "another_value"}
        assert result == expected


def test_collect_env_fields_missing_variable():
    """Test _collect_env_fields with missing environment variable."""
    env_fields = {"MISSING_VAR": "missing"}

    with pytest.raises(
        EnvironmentVariableError, match="Required environment variable 'MISSING_VAR' is not set"
    ):
        _collect_env_fields(env_fields=env_fields)


def test_collect_env_fields_with_prefix():
    """Test _collect_env_fields with env_prefix."""
    with patch.dict(os.environ, {"APP_SERVICE": "my-service", "APP_VERSION": "1.0", "OTHER_VAR": "ignored"}):
        result = _collect_env_fields(env_prefix="APP_")

        expected = {"service": "my-service", "version": "1.0"}
        assert result == expected


def test_collect_env_fields_combined():
    """Test _collect_env_fields with both env_fields and env_prefix."""
    with patch.dict(
        os.environ, {"SERVICE_NAME": "explicit-service", "APP_VERSION": "1.0", "APP_ENV": "prod"}
    ):
        env_fields = {"SERVICE_NAME": "service"}
        result = _collect_env_fields(env_fields=env_fields, env_prefix="APP_")

        expected = {"service": "explicit-service", "version": "1.0", "env": "prod"}
        assert result == expected


def test_configure_with_env_fields():
    """Test configure with environment fields."""
    with patch.dict(os.environ, {"SERVICE_NAME": "test-service", "VERSION": "1.0.0"}):
        env_fields = {"SERVICE_NAME": "service", "VERSION": "version"}
        configure(env_fields=env_fields)

        root_logger = logging.getLogger()
        handler = root_logger.handlers[0]
        formatter = handler.formatter

        expected_extra_fields = {"service": "test-service", "version": "1.0.0"}
        assert formatter.extra_fields == expected_extra_fields


def test_configure_with_env_prefix():
    """Test configure with environment prefix."""
    with patch.dict(os.environ, {"APP_SERVICE": "my-service", "APP_VERSION": "2.0"}):
        configure(env_prefix="APP_")

        root_logger = logging.getLogger()
        handler = root_logger.handlers[0]
        formatter = handler.formatter

        expected_extra_fields = {"service": "my-service", "version": "2.0"}
        assert formatter.extra_fields == expected_extra_fields


def test_configure_combines_extra_fields_and_env():
    """Test that configure combines extra_fields with environment variables."""
    with patch.dict(os.environ, {"SERVICE_NAME": "env-service"}):
        extra_fields = {"component": "api"}
        env_fields = {"SERVICE_NAME": "service"}

        configure(extra_fields=extra_fields, env_fields=env_fields)

        root_logger = logging.getLogger()
        handler = root_logger.handlers[0]
        formatter = handler.formatter

        expected = {"component": "api", "service": "env-service"}
        assert formatter.extra_fields == expected


def test_configure_env_overrides_extra_fields():
    """Test that environment variables override extra_fields with same key."""
    with patch.dict(os.environ, {"SERVICE_NAME": "env-service"}):
        extra_fields = {"service": "static-service"}  # Should be overridden
        env_fields = {"SERVICE_NAME": "service"}

        configure(extra_fields=extra_fields, env_fields=env_fields)

        root_logger = logging.getLogger()
        handler = root_logger.handlers[0]
        formatter = handler.formatter

        # Environment should win
        assert formatter.extra_fields["service"] == "env-service"


@pytest.mark.parametrize("timestamp_format", ["iso", "epoch"])
def test_configure_timestamp_format(timestamp_format):
    """Test configure with different timestamp formats."""
    configure(timestamp_format=timestamp_format)

    root_logger = logging.getLogger()
    handler = root_logger.handlers[0]
    formatter = handler.formatter

    assert formatter.timestamp_format == timestamp_format


def test_multiple_configure_calls():
    """Test that multiple configure calls work correctly."""
    # First configuration
    configure(level="DEBUG")
    assert logging.getLogger().level == logging.DEBUG

    # Second configuration should override
    configure(level="WARNING")
    assert logging.getLogger().level == logging.WARNING

    # Should still have only one handler
    assert len(logging.getLogger().handlers) == 1
