"""
JSON formatter for structured logging.

This module provides the StructFormatter class, which converts log records
into structured JSON format with consistent standard fields and support
for additional structured data.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union


class StructFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.

    This formatter converts log records into structured JSON format with
    consistent standard fields (timestamp, level, logger, message) and
    includes any additional structured fields passed to logging methods.

    Examples:
        Basic usage:
        >>> formatter = StructFormatter()
        >>> handler.setFormatter(formatter)

        With custom timestamp format:
        >>> formatter = StructFormatter(timestamp_format="epoch")

        With static extra fields:
        >>> formatter = StructFormatter(extra_fields={"service": "my-app", "version": "1.0"})
    """

    # Standard logging fields that should not be included in context
    STANDARD_FIELDS = {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "getMessage",
        "exc_info",
        "exc_text",
        "stack_info",
        "taskName",
    }

    def __init__(self, timestamp_format: str = "iso", extra_fields: Optional[Dict[str, Any]] = None):
        """
        Initialize the StructFormatter.

        Args:
            timestamp_format: Format for timestamps ("iso" for ISO 8601, "epoch" for Unix timestamp)
            extra_fields: Static fields to include in every log entry

        Examples:
            >>> formatter = StructFormatter()  # Default ISO timestamps
            >>> formatter = StructFormatter(timestamp_format="epoch")
            >>> formatter = StructFormatter(extra_fields={"service": "my-service"})
        """
        super().__init__()
        self.timestamp_format = timestamp_format
        self.extra_fields = extra_fields or {}

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        Args:
            record: The log record to format

        Returns:
            JSON string representation of the log record
        """
        log_entry: Dict[str, Any] = {
            "timestamp": self._format_timestamp(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Build context
        context = {}

        # Add thread-local context first
        from .context import get_context

        context.update(get_context())

        # Add static extra fields
        context.update(self.extra_fields)

        # Add structured fields from record
        for key, value in record.__dict__.items():
            if key not in self.STANDARD_FIELDS:
                context[key] = value

        # Only add context if it has content
        if context:
            log_entry["context"] = context

        return json.dumps(log_entry, default=str, ensure_ascii=False)

    def _format_timestamp(self, record: logging.LogRecord) -> Union[str, float]:
        """
        Format timestamp according to configured format.

        Args:
            record: The log record containing the timestamp

        Returns:
            Formatted timestamp string

        Examples:
            ISO format: "2025-01-01T12:00:00+00:00"
            Epoch format: 1704110400.123
        """
        if self.timestamp_format == "iso":
            return datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()
        else:
            return record.created
