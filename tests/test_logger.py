"""
Tests for structlogger.logger module.

Tests the StructLogger class and its structured logging capabilities.
"""

import logging
from unittest.mock import MagicMock

import pytest

from logstructor.logger import StructLogger


@pytest.fixture
def logger():
    """Create a StructLogger instance for testing."""
    logger = StructLogger("test_logger")
    handler = MagicMock()
    handler.level = logging.DEBUG  # Fix: Set level attribute
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger


@pytest.fixture
def handler(logger):
    """Get the mock handler from the logger."""
    return logger.handlers[0]


def test_logger_inheritance(logger):
    """Test that StructLogger inherits from logging.Logger."""
    assert isinstance(logger, logging.Logger)
    assert isinstance(logger, StructLogger)


def test_standard_logging_compatibility(logger, handler):
    """Test that standard logging methods work unchanged."""
    logger.info("Test message")

    # Verify handler was called
    handler.handle.assert_called_once()
    record = handler.handle.call_args[0][0]

    assert record.getMessage() == "Test message"
    assert record.levelname == "INFO"


def test_structured_fields_in_extra(logger, handler):
    """Test that structured fields are added to log record."""
    logger.info("User action", user_id=123, action="login")

    # Verify handler was called
    handler.handle.assert_called_once()
    record = handler.handle.call_args[0][0]

    assert record.getMessage() == "User action"
    assert record.user_id == 123
    assert record.action == "login"


def test_mixed_extra_and_structured_fields(logger, handler):
    """Test mixing standard extra dict with structured fields."""
    logger.info("Mixed test", extra={"request_id": "req-123"}, user_id=456, action="test")

    record = handler.handle.call_args[0][0]

    # Both extra and structured fields should be present
    assert record.request_id == "req-123"
    assert record.user_id == 456
    assert record.action == "test"


def test_structured_fields_override_extra(logger, handler):
    """Test that structured fields override extra dict fields."""
    logger.info(
        "Override test",
        extra={"user_id": 999},
        user_id=123,  # This should override the extra value
    )

    record = handler.handle.call_args[0][0]
    assert record.user_id == 123  # Structured field wins


@pytest.mark.parametrize(
    "log_method,expected_level",
    [
        ("debug", "DEBUG"),
        ("info", "INFO"),
        ("warning", "WARNING"),
        ("error", "ERROR"),
        ("critical", "CRITICAL"),
    ],
)
def test_all_log_levels_support_structured_fields(logger, handler, log_method, expected_level):
    """Test that all log levels support structured fields."""
    handler.reset_mock()

    method = getattr(logger, log_method)
    method("Test message", test_field="test_value")

    record = handler.handle.call_args[0][0]
    assert record.levelname == expected_level
    assert record.test_field == "test_value"


def test_standard_logging_parameters_work(logger, handler):
    """Test that standard logging parameters (exc_info, stack_info, etc.) work."""
    try:
        raise ValueError("Test exception")
    except ValueError:
        logger.error("Error occurred", exc_info=True, stack_info=True, error_code=500)

    record = handler.handle.call_args[0][0]

    # Standard parameters should work
    assert record.exc_info is not None
    assert record.stack_info is not None  # stack_info is a string, not boolean

    # Structured fields should also work
    assert record.error_code == 500


def test_prepare_extra_with_none_extra(logger):
    """Test _prepare_extra method with None extra."""
    result = logger._prepare_extra(None, {"user_id": 123})
    assert result == {"user_id": 123}


def test_prepare_extra_with_existing_extra(logger):
    """Test _prepare_extra method with existing extra dict."""
    extra = {"request_id": "req-123"}
    struct_fields = {"user_id": 123}

    result = logger._prepare_extra(extra, struct_fields)
    expected = {"request_id": "req-123", "user_id": 123}

    assert result == expected


def test_prepare_extra_with_empty_struct_fields(logger):
    """Test _prepare_extra method with empty structured fields."""
    extra = {"request_id": "req-123"}

    result = logger._prepare_extra(extra, {})
    assert result == dict(extra)


def test_prepare_extra_with_none_extra_and_empty_struct_fields(logger):
    """Test _prepare_extra method with None extra and empty structured fields."""
    result = logger._prepare_extra(None, {})
    assert result is None
