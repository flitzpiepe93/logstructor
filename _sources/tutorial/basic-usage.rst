Basic Usage
===========

This guide covers all the fundamental features of LogStructor and how to use them effectively.

Logger Creation
---------------

LogStructor provides a drop-in replacement for Python's standard logging with automatic JSON formatting:

.. code-block:: python

    import logstructor

    # Create a logger - automatically configured with JSON output
    logger = logstructor.getLogger(__name__)

    # Or with a custom name
    logger = logstructor.getLogger("my_app")

    # Logs are automatically structured JSON - no manual setup needed!
    logger.info("User action", user_id=123, action="login")

Logging Methods
---------------

LogStructor supports all standard logging levels with structured field support:

Debug
~~~~~

.. code-block:: python

    logger.debug(
        "Debugging info", 
        variable_name="user_data", 
        variable_value={"id": 123, "name": "alice"}
    )

Info
~~~~

.. code-block:: python

    logger.info(
        "User action completed", 
        user_id=123, 
        action="profile_update", 
        duration_ms=150
    )

Warning
~~~~~~~

.. code-block:: python

    logger.warning(
        "Rate limit approaching", 
        user_id=456, 
        current_requests=95, 
        limit=100, 
        window_minutes=60
    )

Error
~~~~~

.. code-block:: python

    logger.error(
        "Payment processing failed", 
        transaction_id="txn_789", 
        error_code="INSUFFICIENT_FUNDS", 
        amount=250.00, 
        account_balance=180.50
    )

Critical
~~~~~~~~

.. code-block:: python

    logger.critical(
        "System shutdown initiated", 
        reason="out_of_memory", 
        available_mb=0, 
        required_mb=1024
    )

Structured Fields
-----------------

Add structured data using keyword arguments:

Basic Types
~~~~~~~~~~~

.. code-block:: python

    logger.info(
        "Data types example",
        string_field="hello world",
        integer_field=42,
        float_field=3.14159,
        boolean_field=True,
        none_field=None
    )

Complex Types
~~~~~~~~~~~~~

.. code-block:: python

    from datetime import datetime

    logger.info(
        "Complex data example",
        timestamp=datetime.now(),
        list_field=[1, 2, 3, "four"],
        dict_field={"nested": "value", "count": 5},
        user_data={
            "id": 123,
            "preferences": {
                "theme": "dark",
                "notifications": True
            }
        }
    )

Backward Compatibility
----------------------

All standard logging features continue to work:

String Formatting
~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Standard string formatting
    logger.info("User %s logged in", username)
    logger.info("Processing order {} for customer {}", order_id, customer_id)

    # f-strings
    logger.info(f"User {username} logged in from {ip_address}")

Exception Information
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    try:
        risky_operation()
    except Exception as e:
        logger.error(
            "Operation failed", 
            exc_info=True,  # Include traceback
            operation="data_processing",
            error_type=type(e).__name__
        )

Stack Information
~~~~~~~~~~~~~~~~~

.. code-block:: python

    logger.debug(
        "Debug checkpoint", 
        stack_info=True,  # Include stack trace
        checkpoint="data_validation"
    )

Extra Fields (Standard Logging)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Standard logging extra parameter still works
    logger.info(
        "Standard extra", 
        extra={"request_id": "req-123"},
        user_id=456
    )

Combining Standard and Structured
----------------------------------

You can mix standard logging patterns with structured fields:

.. code-block:: python

    # Message with formatting + structured fields
    logger.info(
        "User %s performed action", username,
        user_id=123,
        action="login",
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0..."
    )

    # Exception handling with structured context
    try:
        process_payment(amount, card_token)
    except PaymentError as e:
        logger.error(
            "Payment failed: %s", str(e),
            exc_info=True,
            payment_id=payment_id,
            amount=amount,
            error_code=e.code,
            retry_count=retry_count
        )

Data Serialization
------------------

LogStructor automatically handles data serialization:

Automatic Conversion
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from datetime import datetime, date
    from decimal import Decimal

    logger.info(
        "Serialization example",
        timestamp=datetime.now(),        # → ISO string
        date_field=date.today(),         # → ISO date string
        decimal_field=Decimal("99.99"),  # → float
        custom_object=MyClass()          # → str(object)
    )

Custom Objects
~~~~~~~~~~~~~~

.. code-block:: python

    class User:
        def __init__(self, id, name):
            self.id = id
            self.name = name
        
        def __str__(self):
            return f"User({self.id}, {self.name})"

    user = User(123, "alice")
    logger.info("User created", user_object=user)  # Uses __str__

Integration Examples
--------------------

Web Framework Integration
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from flask import Flask, request
    import logstructor

    app = Flask(__name__)
    logger = logstructor.getLogger(__name__)

    @app.route('/api/users/<int:user_id>')
    def get_user(user_id):
        logger.info("API request received",
                   endpoint="/api/users",
                   method=request.method,
                   user_id=user_id,
                   ip_address=request.remote_addr,
                   user_agent=request.headers.get('User-Agent'))
        
        # Process request...
        
        logger.info("API request completed",
                   status_code=200,
                   response_time_ms=150)

Database Integration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import time

    def execute_query(sql, params=None):
        start_time = time.time()
        
        try:
            logger.debug("Executing query", 
                        sql=sql, 
                        params=params)
            
            # Execute query...
            result = cursor.execute(sql, params)
            
            duration = (time.time() - start_time) * 1000
            logger.info("Query completed",
                       query_duration_ms=round(duration, 2),
                       rows_affected=cursor.rowcount)
            
            return result
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error("Query failed",
                        exc_info=True,
                        sql=sql,
                        query_duration_ms=round(duration, 2),
                        error_type=type(e).__name__)
            raise

Async Usage
-----------

LogStructor works seamlessly with async/await:

.. code-block:: python

    import asyncio
    import logstructor

    logger = logstructor.getLogger(__name__)

    async def handle_request():
        logstructor.bind_context(request_id="req-123")
        
        await authenticate_user()  # Context preserved across await
        logger.info("User authenticated")
        
        await process_data()       # Still has request_id
        logger.info("Processing complete")
        
        logstructor.clear_context()

    # Context is isolated between concurrent tasks
    async def main():
        tasks = [handle_request() for _ in range(10)]
        await asyncio.gather(*tasks)  # Each task has its own context

Next Steps
----------

- :doc:`json-formatting` - Configure structured JSON output
- :doc:`context-management` - Learn about context management
- :doc:`best-practices` - Optimal patterns and techniques