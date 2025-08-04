"""
Context management for structured logging using contextvars.

This module provides functions to bind context data to the current context,
which will be automatically included in all log entries within that context.
This works with both synchronous and asynchronous code and is the modern
replacement for thread-local storage. It's particularly useful for web
applications where you want to include request-specific data (like request_id,
user_id) in all logs without passing them explicitly to every logging call.
"""

import contextvars
from typing import Any, Dict

# Context variable for storing logging context data
_context_data: contextvars.ContextVar[Dict[str, Any]] = contextvars.ContextVar("logging_context", default={})


def bind_context(**kwargs) -> None:
    """
    Bind key-value pairs to the current context's logging context.

    These fields will be automatically included in all subsequent log entries
    within the current context until cleared or overwritten. Works with both
    synchronous and asynchronous code.

    Args:
        **kwargs: Key-value pairs to bind to the context

    Examples:
        Basic usage:
        >>> bind_context(request_id="req-123", user_id=456)
        >>> logger.info("Processing request")  # Will include request_id and user_id

        Web application example:
        >>> bind_context(request_id=request.id, user_id=request.user.id, ip=request.remote_addr)
        >>> logger.info("User login attempt")  # Automatically includes all context

        Async usage:
        >>> async def handle_request():
        ...     bind_context(request_id="req-123")
        ...     await process_request()  # Context is preserved across await calls

        Overwriting context:
        >>> bind_context(user_id=123)
        >>> bind_context(user_id=456)  # Overwrites previous user_id
    """
    current_context = _context_data.get().copy()
    current_context.update(kwargs)
    _context_data.set(current_context)


def clear_context() -> None:
    """
    Clear all context data for the current context.

    This removes all previously bound context fields. Subsequent log entries
    will not include any context data until new fields are bound.

    Examples:
        >>> bind_context(user_id=123, request_id="req-456")
        >>> logger.info("With context")  # Includes user_id and request_id
        >>> clear_context()
        >>> logger.info("Without context")  # No context fields

        Cleanup after request:
        >>> def handle_request():
        ...     bind_context(request_id=generate_id())
        ...     # ... process request ...
        ...     clear_context()  # Clean up when done

        Async cleanup:
        >>> async def handle_async_request():
        ...     bind_context(request_id=generate_id())
        ...     try:
        ...         await process_request()
        ...     finally:
        ...         clear_context()  # Always clean up
    """
    _context_data.set({})


def get_context() -> Dict[str, Any]:
    """
    Get current context's context data.

    Returns a copy of the current context dictionary. This is primarily
    used internally by the formatter, but can be useful for debugging
    or conditional logic based on current context.

    Returns:
        Dictionary of current context fields (copy, not reference)

    Examples:
        >>> bind_context(user_id=123, role="admin")
        >>> current = get_context()
        >>> print(current)  # {'user_id': 123, 'role': 'admin'}

        Conditional logging:
        >>> context = get_context()
        >>> if context.get('user_id'):
        ...     logger.info("User-specific operation")
        ... else:
        ...     logger.info("Anonymous operation")

        Async usage:
        >>> async def some_async_function():
        ...     context = get_context()
        ...     if context.get('request_id'):
        ...         await log_request_specific_data()
    """
    return _context_data.get().copy()


def update_context(**kwargs) -> None:
    """
    Update existing context with new key-value pairs.

    This is an alias for bind_context() - both functions do the same thing.
    Use whichever name feels more natural in your code.

    Args:
        **kwargs: Key-value pairs to add/update in the context

    Examples:
        >>> bind_context(request_id="req-123")
        >>> update_context(user_id=456, action="login")
        >>> # Context now has: request_id, user_id, action

        Async example:
        >>> async def process_user_action():
        ...     bind_context(request_id="req-123")
        ...     await authenticate_user()
        ...     update_context(user_id=456, authenticated=True)
        ...     await perform_action()
    """
    bind_context(**kwargs)
