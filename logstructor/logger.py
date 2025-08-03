"""
Enhanced logger with structured logging capabilities.

This module provides the StructLogger class, which extends Python's standard
logging.Logger to support structured logging while maintaining 100% backward
compatibility with the standard logging API.
"""

import logging
from types import TracebackType
from typing import Any, Dict, Mapping, Optional, Union


class StructLogger(logging.Logger):
    """
    Enhanced logger with structured logging capabilities.

    This logger extends the standard logging.Logger to support structured logging
    by accepting keyword arguments that are automatically added as structured fields
    to log records. It maintains 100% backward compatibility with the standard
    logging API.

    Examples:
        Basic usage (backward compatible):
        >>> logger = StructLogger("my_logger")
        >>> logger.info("User logged in")

        Structured logging:
        >>> logger.info("User logged in", user_id=123, ip="192.168.1.1")

        Mixed usage:
        >>> logger.error("Database error", exc_info=True, error_code=500, retry_count=3)
    """

    def __init__(self, name: str, level: int = logging.NOTSET):
        """
        Initialize the StructLogger.

        Args:
            name: The name of the logger (same as standard logging)
            level: The logging level (same as standard logging)
        """
        super().__init__(name, level)

    def _prepare_extra(
        self, extra: Optional[Mapping[str, object]], struct_fields: Dict[str, Any]
    ) -> Optional[Dict[str, object]]:
        """
        Prepare extra dict by merging in structured fields.

        This helper method combines the existing extra dict (if any) with the
        structured fields passed as keyword arguments to logging methods.

        Args:
            extra: Existing extra dict from standard logging parameters
            struct_fields: Structured fields passed as keyword arguments

        Returns:
            Combined extra dict, or None if no structured fields and no existing extra

        Examples:
            >>> logger._prepare_extra(None, {"user_id": 123})
            {"user_id": 123}

            >>> logger._prepare_extra({"request_id": "abc"}, {"user_id": 123})
            {"request_id": "abc", "user_id": 123}
        """
        if struct_fields:
            if extra is None:
                return struct_fields
            else:
                return {**dict(extra), **struct_fields}
        return dict(extra) if extra is not None else None

    def debug(
        self,
        msg: object,
        *args: object,
        exc_info: Union[
            bool,
            tuple[type[BaseException], BaseException, TracebackType | None],
            tuple[None, None, None],
            BaseException,
            None,
        ] = None,
        extra: Optional[Mapping[str, object]] = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        **struct_fields: Any,
    ) -> None:
        """
        Log a message with severity 'DEBUG' and optional structured fields.

        This method extends the standard debug() method to accept structured fields
        as keyword arguments while maintaining full backward compatibility.

        Args:
            msg: The message to log
            *args: Arguments for string formatting (same as standard logging)
            exc_info: Exception info (same as standard logging)
            extra: Extra fields dict (same as standard logging)
            stack_info: Include stack info (same as standard logging)
            stacklevel: Stack level for caller info (same as standard logging)
            **struct_fields: Structured fields to add to the log record

        Examples:
            >>> logger.debug("Processing request")
            >>> logger.debug("User action", user_id=123, action="click")
            >>> logger.debug("Error occurred", exc_info=True, error_code=404)
        """
        extra = self._prepare_extra(extra, struct_fields)
        super().debug(
            msg, *args, exc_info=exc_info, extra=extra, stack_info=stack_info, stacklevel=stacklevel
        )

    def info(
        self,
        msg: object,
        *args: object,
        exc_info: Union[
            bool,
            tuple[type[BaseException], BaseException, TracebackType | None],
            tuple[None, None, None],
            BaseException,
            None,
        ] = None,
        extra: Optional[Mapping[str, object]] = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        **struct_fields: Any,
    ) -> None:
        """
        Log a message with severity 'INFO' and optional structured fields.

        This method extends the standard info() method to accept structured fields
        as keyword arguments while maintaining full backward compatibility.

        Args:
            msg: The message to log
            *args: Arguments for string formatting (same as standard logging)
            exc_info: Exception info (same as standard logging)
            extra: Extra fields dict (same as standard logging)
            stack_info: Include stack info (same as standard logging)
            stacklevel: Stack level for caller info (same as standard logging)
            **struct_fields: Structured fields to add to the log record

        Examples:
            >>> logger.info("User logged in")
            >>> logger.info("User logged in", user_id=123, ip="192.168.1.1")
            >>> logger.info("Request processed", duration_ms=150, status_code=200)
        """
        extra = self._prepare_extra(extra, struct_fields)
        super().info(msg, *args, exc_info=exc_info, extra=extra, stack_info=stack_info, stacklevel=stacklevel)

    def warning(
        self,
        msg: object,
        *args: object,
        exc_info: Union[
            bool,
            tuple[type[BaseException], BaseException, TracebackType | None],
            tuple[None, None, None],
            BaseException,
            None,
        ] = None,
        extra: Optional[Mapping[str, object]] = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        **struct_fields: Any,
    ) -> None:
        """
        Log a message with severity 'WARNING' and optional structured fields.

        This method extends the standard warning() method to accept structured fields
        as keyword arguments while maintaining full backward compatibility.

        Args:
            msg: The message to log
            *args: Arguments for string formatting (same as standard logging)
            exc_info: Exception info (same as standard logging)
            extra: Extra fields dict (same as standard logging)
            stack_info: Include stack info (same as standard logging)
            stacklevel: Stack level for caller info (same as standard logging)
            **struct_fields: Structured fields to add to the log record

        Examples:
            >>> logger.warning("Deprecated API used")
            >>> logger.warning("Rate limit exceeded", user_id=123, limit=100)
            >>> logger.warning("Slow query", query_time_ms=5000, table="users")
        """
        extra = self._prepare_extra(extra, struct_fields)
        super().warning(
            msg, *args, exc_info=exc_info, extra=extra, stack_info=stack_info, stacklevel=stacklevel
        )

    def error(
        self,
        msg: object,
        *args: object,
        exc_info: Union[
            bool,
            tuple[type[BaseException], BaseException, TracebackType | None],
            tuple[None, None, None],
            BaseException,
            None,
        ] = None,
        extra: Optional[Mapping[str, object]] = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        **struct_fields: Any,
    ) -> None:
        """
        Log a message with severity 'ERROR' and optional structured fields.

        This method extends the standard error() method to accept structured fields
        as keyword arguments while maintaining full backward compatibility.

        Args:
            msg: The message to log
            *args: Arguments for string formatting (same as standard logging)
            exc_info: Exception info (same as standard logging)
            extra: Extra fields dict (same as standard logging)
            stack_info: Include stack info (same as standard logging)
            stacklevel: Stack level for caller info (same as standard logging)
            **struct_fields: Structured fields to add to the log record

        Examples:
            >>> logger.error("Database connection failed")
            >>> logger.error("Authentication failed", user_id=123, reason="invalid_password")
            >>> logger.error("Unexpected error", exc_info=True, error_code=500)
        """
        extra = self._prepare_extra(extra, struct_fields)
        super().error(
            msg, *args, exc_info=exc_info, extra=extra, stack_info=stack_info, stacklevel=stacklevel
        )

    def critical(
        self,
        msg: object,
        *args: object,
        exc_info: Union[
            bool,
            tuple[type[BaseException], BaseException, TracebackType | None],
            tuple[None, None, None],
            BaseException,
            None,
        ] = None,
        extra: Optional[Mapping[str, object]] = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        **struct_fields: Any,
    ) -> None:
        """
        Log a message with severity 'CRITICAL' and optional structured fields.

        This method extends the standard critical() method to accept structured fields
        as keyword arguments while maintaining full backward compatibility.

        Args:
            msg: The message to log
            *args: Arguments for string formatting (same as standard logging)
            exc_info: Exception info (same as standard logging)
            extra: Extra fields dict (same as standard logging)
            stack_info: Include stack info (same as standard logging)
            stacklevel: Stack level for caller info (same as standard logging)
            **struct_fields: Structured fields to add to the log record

        Examples:
            >>> logger.critical("System shutdown initiated")
            >>> logger.critical("Out of memory", available_mb=0, required_mb=1024)
            >>> logger.critical("Security breach detected", source_ip="1.2.3.4", severity="high")
        """
        extra = self._prepare_extra(extra, struct_fields)
        super().critical(
            msg, *args, exc_info=exc_info, extra=extra, stack_info=stack_info, stacklevel=stacklevel
        )
