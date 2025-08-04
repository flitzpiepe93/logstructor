"""
Tests for structlogger.context module.

Tests context management functionality using contextvars.
"""

import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from logstructor.context import bind_context, clear_context, get_context, update_context


@pytest.fixture(autouse=True)
def clear_context_fixture():
    """Clear context before and after each test."""
    clear_context()
    yield
    clear_context()


def test_bind_context_basic():
    """Test basic context binding."""
    bind_context(user_id=123, action="login")

    context = get_context()
    assert context["user_id"] == 123
    assert context["action"] == "login"


def test_bind_context_multiple_calls():
    """Test multiple bind_context calls accumulate."""
    bind_context(user_id=123)
    bind_context(action="login")

    context = get_context()
    assert context["user_id"] == 123
    assert context["action"] == "login"


def test_bind_context_overwrites_existing():
    """Test that bind_context overwrites existing keys."""
    bind_context(user_id=123)
    bind_context(user_id=456)  # Should overwrite

    context = get_context()
    assert context["user_id"] == 456


def test_clear_context():
    """Test context clearing."""
    bind_context(user_id=123, action="login")
    assert len(get_context()) == 2

    clear_context()
    assert len(get_context()) == 0


def test_get_context_returns_copy():
    """Test that get_context returns a copy, not reference."""
    bind_context(user_id=123)

    context1 = get_context()
    context2 = get_context()

    # Should be equal but not the same object
    assert context1 == context2
    assert context1 is not context2

    # Modifying one shouldn't affect the other
    context1["new_key"] = "new_value"
    assert "new_key" not in get_context()


def test_update_context_alias():
    """Test that update_context is an alias for bind_context."""
    update_context(user_id=123)

    context = get_context()
    assert context["user_id"] == 123


def test_empty_context_initially():
    """Test that context is empty initially."""
    context = get_context()
    assert len(context) == 0
    assert isinstance(context, dict)


def test_context_isolation_between_threads():
    """Test that context is isolated between threads with contextvars."""
    results = {}

    def thread_function(thread_id):
        # Each thread sets its own context
        bind_context(thread_id=thread_id, data=f"thread-{thread_id}")

        # Small delay to ensure threads are running concurrently
        time.sleep(0.1)

        # Get context and store result
        results[thread_id] = get_context()

    # Start multiple threads
    threads = []
    for i in range(3):
        thread = threading.Thread(target=thread_function, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Verify each thread had its own context
    assert len(results) == 3
    for i in range(3):
        assert results[i]["thread_id"] == i
        assert results[i]["data"] == f"thread-{i}"


def test_thread_pool_isolation():
    """Test context isolation with ThreadPoolExecutor."""

    def worker_function(worker_id):
        bind_context(worker_id=worker_id)
        time.sleep(0.05)  # Small delay
        return get_context()

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(worker_function, i) for i in range(5)]
        results = [future.result() for future in futures]

    # Each worker should have its own context
    for i, result in enumerate(results):
        assert result["worker_id"] == i


def test_context_survives_across_function_calls():
    """Test that context persists across function calls in same thread."""

    def set_context():
        bind_context(user_id=123)

    def get_user_id():
        return get_context().get("user_id")

    set_context()
    user_id = get_user_id()

    assert user_id == 123


@pytest.mark.parametrize(
    "value,expected",
    [
        ("test", "test"),
        (123, 123),
        (45.67, 45.67),
        (True, True),
        (None, None),
        ([1, 2, 3], [1, 2, 3]),
        ({"nested": "value"}, {"nested": "value"}),
    ],
)
def test_bind_context_with_various_types(value, expected):
    """Test binding context with various data types."""
    bind_context(test_value=value)

    context = get_context()
    assert context["test_value"] == expected


def test_context_with_empty_values():
    """Test context with empty/falsy values."""
    bind_context(empty_string="", zero=0, false_val=False, empty_list=[], empty_dict={})

    context = get_context()

    # All values should be preserved, even falsy ones
    assert context["empty_string"] == ""
    assert context["zero"] == 0
    assert context["false_val"] is False
    assert context["empty_list"] == []
    assert context["empty_dict"] == {}


@pytest.mark.asyncio
async def test_async_context_isolation():
    """Test that context is properly isolated in async functions."""
    results = {}

    async def async_function(task_id):
        # Each async task sets its own context
        bind_context(task_id=task_id, data=f"task-{task_id}")

        # Simulate async work
        await asyncio.sleep(0.1)

        # Context should be preserved across await
        results[task_id] = get_context()

    # Run multiple async tasks concurrently
    tasks = [async_function(i) for i in range(3)]
    await asyncio.gather(*tasks)

    # Verify each task had its own context
    assert len(results) == 3
    for i in range(3):
        assert results[i]["task_id"] == i
        assert results[i]["data"] == f"task-{i}"


@pytest.mark.asyncio
async def test_async_context_persistence():
    """Test that context persists across multiple await calls."""
    bind_context(request_id="req-123", user_id=456)

    async def check_context():
        await asyncio.sleep(0.01)
        return get_context()

    # Context should persist across multiple async calls
    context1 = await check_context()
    context2 = await check_context()

    assert context1["request_id"] == "req-123"
    assert context1["user_id"] == 456
    assert context2 == context1


@pytest.mark.asyncio
async def test_async_context_updates():
    """Test updating context in async functions."""
    bind_context(request_id="req-123")

    async def update_user_context():
        await asyncio.sleep(0.01)
        update_context(user_id=456, authenticated=True)

    await update_user_context()

    context = get_context()
    assert context["request_id"] == "req-123"
    assert context["user_id"] == 456
    assert context["authenticated"] is True
