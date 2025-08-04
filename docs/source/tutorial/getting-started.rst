Getting Started
===============

This guide will get you up and running with LogStructor in under 5 minutes.

.. code-block:: bash

    pip install logstructor

Your First Structured Log
-------------------------

Replace your standard logging import:

.. code-block:: python

    # Before
    import logging
    logger = logging.getLogger(__name__)

    # After
    import logstructor
    logger = logstructor.getLogger(__name__)

That's it! Your existing logging code continues to work unchanged.

Adding Structure
----------------

Now enhance your logs with structured fields:

.. code-block:: python

    import logstructor

    logger = logstructor.getLogger(__name__)

    # Standard logging still works
    logger.info("Application started")

    # Add structured fields as keyword arguments
    logger.error(
        "Database connection failed", 
        host="db.example.com", 
        port=5432, 
        timeout_seconds=30,
        retry_count=3
    )

LogStructor automatically configures JSON output - no manual setup needed:

Custom Configuration (Optional)
-------------------------------

If you need custom settings, use ``configure()``:

.. code-block:: python

    import logstructor

    # Optional: Custom configuration
    logstructor.configure(
        level="DEBUG",
        extra_fields={
            "service": "user-api",
            "version": "1.2.3"
        }
    )

    logger = logstructor.getLogger(__name__)

Context Management
------------------

For web applications, use context to automatically include request-specific data:

.. code-block:: python

    import logstructor

    logger = logstructor.getLogger(__name__)

    def handle_request(request):
        # Set context once per request
        logstructor.bind_context(
            request_id=request.id,
            user_id=request.user.id,
            ip_address=request.remote_addr
        )
        
        try:
            # All logs automatically include the context
            logger.info("Processing request")
            logger.info("Validating input", field="email")
            logger.info("Database query", table="users", duration_ms=45)
            logger.info("Request completed", status_code=200)
            
        finally:
            # Clean up context when done
            logstructor.clear_context()

Async Support
-------------

LogStructor works seamlessly with async/await:

.. code-block:: python

    import asyncio
    import logstructor

    logger = logstructor.getLogger(__name__)

    async def handle_async_request():
        logstructor.bind_context(request_id="req-123")
        
        await authenticate_user()  # Context preserved across await
        logger.info("User authenticated")
        
        await process_data()       # Still has request_id
        logger.info("Processing complete")
        
        logstructor.clear_context()

    # Context is isolated between concurrent tasks
    async def main():
        tasks = [handle_async_request() for _ in range(10)]
        await asyncio.gather(*tasks)  # Each task has its own context

Next Steps
----------

Now that you have LogStructor running, explore these guides to get the most out of structured logging:

**Essential Reading:**

- :doc:`basic-usage` - Learn all the fundamental features and patterns
- :doc:`context-management` - Master request-scoped context for web apps
- :doc:`json-formatting` - Understand JSON output and log aggregator integration

**Advanced Topics:**

- :doc:`best-practices` - Production-ready patterns and performance optimization

**Quick Reference:**

.. code-block:: python

    import logstructor

    # Get a logger (automatically configured)
    logger = logstructor.getLogger(__name__)

    # Log with structured fields
    logger.info("User action", user_id=123, action="login")

    # Set context for automatic inclusion
    logstructor.bind_context(request_id="req-123")
    logger.info("Processing")  # Includes request_id automatically

    # Clean up when done
    logstructor.clear_context()

**Common Use Cases:**

- **Web APIs**: Add request_id, user_id to every log
- **Microservices**: Include service name, version in all logs  
- **Error Tracking**: Structure error logs for better analysis
- **Performance Monitoring**: Log response times, query durations
- **Async Applications**: Full support for asyncio and concurrent tasks

Ready to dive deeper? Start with :doc:`basic-usage` to learn all the features!
