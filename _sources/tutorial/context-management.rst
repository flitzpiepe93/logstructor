Context Management
==================

LogStructor's context management allows you to bind data to the current context, which is then automatically included in all subsequent log entries. This is particularly powerful for web applications where you want request-specific data in every log.

Basic Context Usage
-------------------

Binding Context
~~~~~~~~~~~~~~~

Use ``bind_context()`` to add fields that will be included in all logs:

.. code-block:: python

    import logstructor

    logger = logstructor.getLogger(__name__)

    # Bind context data
    logstructor.bind_context(
        request_id="req-abc123",
        user_id=456,
        session_id="sess-xyz789"
    )

    # All subsequent logs include the context automatically
    logger.info("Processing request")
    logger.info("Validating input", field="email")
    logger.info("Database query", table="users")
    logger.info("Request completed", status_code=200)

**Output (with JSON formatter):**

.. code-block:: json

    {
      "timestamp": "2025-01-08T10:30:45Z",
      "level": "INFO",
      "logger": "__main__",
      "message": "Processing request",
      "context": {
        "request_id": "req-abc123",
        "user_id": 456,
        "session_id": "sess-xyz789"
      }
    }

Clearing Context
~~~~~~~~~~~~~~~~

Always clear context when done to prevent data leakage:

.. code-block:: python

    # Clear all context data
    logstructor.clear_context()

    # Logs no longer include the previous context
    logger.info("Context cleared")  # No context fields

Viewing Current Context
~~~~~~~~~~~~~~~~~~~~~~~

Check what's currently in context:

.. code-block:: python

    # Get current context as a dictionary
    current_context = logstructor.get_context()
    print(current_context)
    # Output: {'request_id': 'req-abc123', 'user_id': 456, 'session_id': 'sess-xyz789'}

Context Isolation
-----------------

Context is automatically isolated between different execution contexts, including threads and async tasks:

Thread Isolation
~~~~~~~~~~~~~~~~

.. code-block:: python

    import threading
    import time

    def worker_function(worker_id):
        # Each thread sets its own context
        logstructor.bind_context(
            worker_id=worker_id,
            thread_name=threading.current_thread().name
        )
        
        logger.info("Worker started")
        time.sleep(1)  # Simulate work
        logger.info("Worker completed")
        
        # Clean up this thread's context
        logstructor.clear_context()

    # Start multiple threads
    for i in range(3):
        thread = threading.Thread(target=worker_function, args=(i,))
        thread.start()

Each thread's logs will only include its own context data.

Async Task Isolation
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import asyncio
    import logstructor

    logger = logstructor.getLogger(__name__)

    async def async_task(task_id):
        # Each async task has its own context
        logstructor.bind_context(task_id=task_id)
        
        await asyncio.sleep(0.1)  # Context preserved across await
        logger.info("Task processing")
        
        await asyncio.sleep(0.1)  # Still has task_id
        logger.info("Task completed")
        
        logstructor.clear_context()

    # Run multiple tasks concurrently - each has isolated context
    async def main():
        tasks = [async_task(i) for i in range(5)]
        await asyncio.gather(*tasks)

Web Application Patterns
-------------------------

Flask Integration
~~~~~~~~~~~~~~~~~

.. code-block:: python

    from flask import Flask, request, g
    import logstructor
    import uuid

    app = Flask(__name__)
    logger = logstructor.getLogger(__name__)

    @app.before_request
    def before_request():
        # Generate unique request ID
        g.request_id = str(uuid.uuid4())
        
        # Bind request context
        logstructor.bind_context(
            request_id=g.request_id,
            method=request.method,
            path=request.path,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', 'Unknown')
        )
        
        logger.info("Request started")

    @app.after_request
    def after_request(response):
        logger.info("Request completed", 
                   status_code=response.status_code,
                   content_length=response.content_length)
        
        # Clean up context
        logstructor.clear_context()
        return response

    @app.route('/api/users/<int:user_id>')
    def get_user(user_id):
        # Add user-specific context
        logstructor.bind_context(user_id=user_id)
        
        logger.info("Fetching user data")
        # ... business logic ...
        logger.info("User data retrieved", record_count=1)
        
        return {"user_id": user_id, "name": "Alice"}

Django Integration
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # middleware.py
    import logstructor
    import uuid

    class LogContextMiddleware:
        def __init__(self, get_response):
            self.get_response = get_response

        def __call__(self, request):
            # Set up context for this request
            request_id = str(uuid.uuid4())
            
            logstructor.bind_context(
                request_id=request_id,
                method=request.method,
                path=request.path,
                ip_address=self.get_client_ip(request)
            )
            
            # Add user context if authenticated
            if hasattr(request, 'user') and request.user.is_authenticated:
                logstructor.bind_context(user_id=request.user.id)
            
            try:
                response = self.get_response(request)
                return response
            finally:
                # Always clean up context
                logstructor.clear_context()
        
        def get_client_ip(self, request):
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                return x_forwarded_for.split(',')[0]
            return request.META.get('REMOTE_ADDR')

    # views.py
    import logstructor

    logger = logstructor.getLogger(__name__)

    def user_profile(request, user_id):
        logger.info("Fetching user profile")
        # All logs automatically include request context + user_id
        
        try:
            # Business logic
            logger.info("Database query", table="users")
            user = User.objects.get(id=user_id)
            logger.info("Profile retrieved successfully")
            return JsonResponse({"user": user.to_dict()})
            
        except User.DoesNotExist:
            logger.warning("User not found", requested_user_id=user_id)
            return JsonResponse({"error": "User not found"}, status=404)

FastAPI Integration
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from fastapi import FastAPI, Request
    import logstructor
    import uuid

    app = FastAPI()
    logger = logstructor.getLogger(__name__)

    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        # Set up context for this request
        request_id = str(uuid.uuid4())
        
        logstructor.bind_context(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            ip_address=request.client.host
        )
        
        logger.info("Request started")
        
        try:
            response = await call_next(request)
            logger.info("Request completed", status_code=response.status_code)
            return response
        finally:
            logstructor.clear_context()

    @app.get("/users/{user_id}")
    async def get_user(user_id: int):
        logstructor.bind_context(user_id=user_id)
        
        logger.info("Fetching user data")
        # Context is preserved across await calls
        await asyncio.sleep(0.1)  # Simulate async work
        logger.info("User data retrieved")
        
        return {"user_id": user_id, "name": "Alice"}

Context Updates
---------------

Adding More Context
~~~~~~~~~~~~~~~~~~~

You can add more context data at any time:

.. code-block:: python

    # Initial context
    logstructor.bind_context(request_id="req-123")

    logger.info("Request started")

    # Add more context later
    logstructor.bind_context(user_id=456, operation="checkout")

    logger.info("User authenticated")  # Includes request_id + user_id + operation

    # Add even more context
    logstructor.bind_context(cart_items=3, total_amount=99.99)

    logger.info("Processing payment")  # Includes all context fields

Updating Context
~~~~~~~~~~~~~~~~

Use ``update_context()`` (alias for ``bind_context()``):

.. code-block:: python

    # These are equivalent
    logstructor.bind_context(user_id=123)
    logstructor.update_context(user_id=123)

Overwriting Context Fields
~~~~~~~~~~~~~~~~~~~~~~~~~~

Later calls overwrite existing fields:

.. code-block:: python

    logstructor.bind_context(user_id=123, status="pending")
    logger.info("Initial state")  # user_id=123, status="pending"

    logstructor.bind_context(status="completed")  # Overwrites status
    logger.info("Updated state")   # user_id=123, status="completed"

Advanced Patterns
-----------------

Context Managers
~~~~~~~~~~~~~~~~

Create reusable context managers:

.. code-block:: python

    from contextlib import contextmanager

    @contextmanager
    def user_context(user_id, username=None):
        """Context manager for user-specific logging"""
        logstructor.bind_context(user_id=user_id)
        if username:
            logstructor.bind_context(username=username)
        
        try:
            yield
        finally:
            # Context is automatically cleared when exiting
            logstructor.clear_context()

    # Usage
    with user_context(123, "alice"):
        logger.info("Processing user data")
        logger.info("User operation completed")
    # Context automatically cleared here

Nested Contexts
~~~~~~~~~~~~~~~

For complex operations, you might want nested contexts:

.. code-block:: python

    def process_order(order_id, user_id):
        # Set order context
        logstructor.bind_context(order_id=order_id, user_id=user_id)
        
        try:
            logger.info("Order processing started")
            
            # Process each item
            for item_id in get_order_items(order_id):
                # Add item-specific context (temporary)
                logstructor.bind_context(current_item_id=item_id)
                
                logger.info("Processing item")
                process_item(item_id)
                
                # Remove item-specific context
                current_context = logstructor.get_context()
                current_context.pop('current_item_id', None)
                logstructor.clear_context()
                logstructor.bind_context(**current_context)
            
            logger.info("Order processing completed")
            
        finally:
            logstructor.clear_context()

Conditional Context
~~~~~~~~~~~~~~~~~~~

Add context based on conditions:

.. code-block:: python

    def handle_request(request):
        # Always add request context
        logstructor.bind_context(
            request_id=request.id,
            method=request.method
        )
        
        # Add user context if authenticated
        if request.user.is_authenticated:
            logstructor.bind_context(
                user_id=request.user.id,
                user_type=request.user.user_type
            )
        
        # Add admin context for admin users
        if request.user.is_staff:
            logstructor.bind_context(is_admin=True)
        
        # Add debug context in development
        if settings.DEBUG:
            logstructor.bind_context(
                debug_mode=True,
                request_headers=dict(request.headers)
            )
        
        try:
            # Process request
            logger.info("Processing request")
            # ... business logic ...
            
        finally:
            logstructor.clear_context()

Performance Considerations
--------------------------

Context Overhead
~~~~~~~~~~~~~~~~

Context management has minimal performance impact:

.. code-block:: python

    # Benchmark results (approximate)
    # Without context: 100,000 msgs/sec
    # With context:     95,000 msgs/sec
    # Overhead: ~5%

Best Practices
~~~~~~~~~~~~~~

1. **Set context once per request**:

.. code-block:: python

    # Good: Set once
    logstructor.bind_context(request_id="req-123", user_id=456)
    logger.info("Step 1")
    logger.info("Step 2")
    logger.info("Step 3")

    # Avoid: Setting context repeatedly
    logger.info("Step 1", request_id="req-123", user_id=456)
    logger.info("Step 2", request_id="req-123", user_id=456)
    logger.info("Step 3", request_id="req-123", user_id=456)

2. **Always clear context**:

.. code-block:: python

    try:
        logstructor.bind_context(request_id="req-123")
        # ... process request ...
    finally:
        logstructor.clear_context()  # Always clean up

3. **Use simple data types in context**:

.. code-block:: python

    # Good: Simple types
    logstructor.bind_context(user_id=123, action="login")

    # Avoid: Complex objects
    logstructor.bind_context(user_object=complex_user_instance)

Debugging Context
-----------------

Inspecting Context
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Check current context
    context = logstructor.get_context()
    print(f"Current context: {context}")

    # Log current context
    logger.debug("Current context", current_context=context)

Context Validation
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    def validate_context():
        """Ensure required context is present"""
        context = logstructor.get_context()
        required_fields = ['request_id', 'user_id']
        
        missing = [field for field in required_fields if field not in context]
        if missing:
            logger.warning("Missing required context fields", missing_fields=missing)
            return False
        return True

    # Use in request handlers
    if not validate_context():
        logger.error("Request processing aborted due to missing context")
        return error_response()

Common Pitfalls
---------------

Memory Leaks
~~~~~~~~~~~~

**Problem**: Forgetting to clear context

.. code-block:: python

    # BAD: Context never cleared
    def handle_request():
        logstructor.bind_context(request_id="req-123")
        # ... process request ...
        # Context remains in memory!

**Solution**: Always use try/finally

.. code-block:: python

    # GOOD: Context always cleared
    def handle_request():
        try:
            logstructor.bind_context(request_id="req-123")
            # ... process request ...
        finally:
            logstructor.clear_context()

Context Confusion
~~~~~~~~~~~~~~~~~

**Problem**: Expecting context to cross execution boundaries incorrectly

.. code-block:: python

    # BAD: Context won't be available in the new thread
    logstructor.bind_context(user_id=123)

    def background_task():
        logger.info("Background work")  # No context here!

    thread = threading.Thread(target=background_task)
    thread.start()

**Solution**: Pass context explicitly or set it in each execution context

.. code-block:: python

    # GOOD: Set context in each execution context
    def background_task(context_data):
        logstructor.bind_context(**context_data)
        try:
            logger.info("Background work")  # Context available
        finally:
            logstructor.clear_context()

    context_data = logstructor.get_context()
    thread = threading.Thread(target=background_task, args=(context_data,))
    thread.start()

Next Steps
----------

- :doc:`json-formatting` - JSON formatting configuration
- :doc:`best-practices` - Production deployment patterns