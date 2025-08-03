"""
Tests for structlogger.formatter module.

Tests the StructFormatter class and JSON formatting capabilities.
"""

import json
import logging
from datetime import datetime
from unittest.mock import patch

import pytest

from logstructor.formatter import StructFormatter


@pytest.fixture
def formatter():
    """Create a StructFormatter instance for testing."""
    return StructFormatter()


@pytest.fixture
def log_record():
    """Create a LogRecord instance for testing."""
    return logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=42,
        msg="Test message",
        args=(),
        exc_info=None,
    )


def test_formatter_inheritance(formatter):
    """Test that StructFormatter inherits from logging.Formatter."""
    assert isinstance(formatter, logging.Formatter)


def test_basic_json_output(formatter, log_record):
    """Test basic JSON output format."""
    output = formatter.format(log_record)
    data = json.loads(output)

    # Check required fields
    assert "timestamp" in data
    assert "level" in data
    assert "logger" in data
    assert "message" in data

    # Check values
    assert data["level"] == "INFO"
    assert data["logger"] == "test_logger"
    assert data["message"] == "Test message"


@pytest.mark.parametrize(
    "timestamp_format,expected_type",
    [
        ("iso", str),
        ("epoch", (int, float)),
    ],
)
def test_timestamp_formats(log_record, timestamp_format, expected_type):
    """Test different timestamp formats."""
    formatter = StructFormatter(timestamp_format=timestamp_format)
    output = formatter.format(log_record)
    data = json.loads(output)

    assert isinstance(data["timestamp"], expected_type)

    if timestamp_format == "iso":
        # Should be parseable as ISO datetime
        datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))


def test_extra_fields_in_formatter(log_record):
    """Test static extra fields from formatter configuration."""
    extra_fields = {"service": "test-service", "version": "1.0.0"}
    formatter = StructFormatter(extra_fields=extra_fields)

    output = formatter.format(log_record)
    data = json.loads(output)

    # Should have context with extra fields
    assert "context" in data
    assert data["context"]["service"] == "test-service"
    assert data["context"]["version"] == "1.0.0"


def test_structured_fields_in_context(formatter, log_record):
    """Test that structured fields from log record appear in context."""
    # Add structured fields to record
    log_record.user_id = 123
    log_record.action = "login"

    output = formatter.format(log_record)
    data = json.loads(output)

    # Should have context with structured fields
    assert "context" in data
    assert data["context"]["user_id"] == 123
    assert data["context"]["action"] == "login"


def test_context_combines_static_and_dynamic_fields(log_record):
    """Test that context combines static extra fields and dynamic structured fields."""
    extra_fields = {"service": "test-service"}
    formatter = StructFormatter(extra_fields=extra_fields)

    # Add structured fields to record
    log_record.user_id = 123

    output = formatter.format(log_record)
    data = json.loads(output)

    # Context should have both
    assert "context" in data
    assert data["context"]["service"] == "test-service"  # Static
    assert data["context"]["user_id"] == 123  # Dynamic


def test_no_context_when_no_extra_fields(formatter, log_record):
    """Test that context field is omitted when there are no extra fields."""
    output = formatter.format(log_record)
    data = json.loads(output)

    # Should not have context field
    assert "context" not in data


def test_standard_fields_excluded_from_context(formatter, log_record):
    """Test that standard logging fields are not included in context."""
    output = formatter.format(log_record)
    data = json.loads(output)

    # Standard fields should not be in context
    if "context" in data:
        context = data["context"]
        standard_fields = ["name", "msg", "levelname", "pathname", "lineno"]
        for field in standard_fields:
            assert field not in context


@patch("logstructor.context.get_context")
def test_thread_local_context_integration(mock_get_context, formatter, log_record):
    """Test integration with thread-local context."""
    # Mock thread-local context
    mock_get_context.return_value = {"request_id": "req-123"}

    output = formatter.format(log_record)
    data = json.loads(output)

    # Should include thread-local context
    assert "context" in data
    assert data["context"]["request_id"] == "req-123"


def test_json_serialization_of_complex_types(formatter, log_record):
    """Test that complex types are properly serialized."""
    # Add various types to record
    log_record.string_field = "test"
    log_record.int_field = 123
    log_record.float_field = 45.67
    log_record.bool_field = True
    log_record.none_field = None
    log_record.list_field = [1, 2, 3]
    log_record.dict_field = {"nested": "value"}

    output = formatter.format(log_record)
    data = json.loads(output)  # Should not raise exception

    # Verify types are preserved
    context = data["context"]
    assert context["string_field"] == "test"
    assert context["int_field"] == 123
    assert context["float_field"] == 45.67
    assert context["bool_field"] is True
    assert context["none_field"] is None
    assert context["list_field"] == [1, 2, 3]
    assert context["dict_field"] == {"nested": "value"}


def test_format_timestamp_method(log_record):
    """Test _format_timestamp method directly."""
    # Test ISO format
    formatter_iso = StructFormatter(timestamp_format="iso")
    timestamp_iso = formatter_iso._format_timestamp(log_record)
    assert isinstance(timestamp_iso, str)

    # Test epoch format
    formatter_epoch = StructFormatter(timestamp_format="epoch")
    timestamp_epoch = formatter_epoch._format_timestamp(log_record)
    assert isinstance(timestamp_epoch, (int, float))


def test_unicode_handling(formatter, log_record):
    """Test proper handling of unicode characters."""
    log_record.unicode_field = "Hello 世界 🌍"

    output = formatter.format(log_record)
    data = json.loads(output)

    # Unicode should be preserved
    assert data["context"]["unicode_field"] == "Hello 世界 🌍"
