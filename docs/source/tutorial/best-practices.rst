Best Practices
==============

This guide covers proven patterns and techniques for using LogStructor effectively in production environments.

Field Naming Conventions
-------------------------

Use Consistent Field Names
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Establish naming conventions across your application:

.. code-block:: python

    # Good: Consistent snake_case
    logger.info("User action", 
               user_id=123, 
               event_type="login", 
               ip_address="192.168.1.100")

    # Avoid: Mixed naming styles
    logger.info("User action", 
               userId=123,           # camelCase
               event_type="login",   # snake_case
               IPAddress="192.168.1.100")  # PascalCase

Standard Field Names
~~~~~~~~~~~~~~~~~~~~

Use these common field names consistently:

.. code-block:: python

    # User identification
    user_id=123
    username="alice"
    user_email="alice@example.com"
    user_role="admin"

    # Request tracking
    request_id="req-abc123"
    session_id="sess-xyz789"
    correlation_id="corr-456def"

    # Network information
    ip_address="192.168.1.100"
    user_agent="Mozilla/5.0..."
    remote_addr="10.0.0.1"

    # Performance metrics
    duration_ms=150
    response_time_ms=250
    query_time_ms=45
    processing_time_ms=100

    # Business entities
    order_id="ORD-12345"
    transaction_id="txn-67890"
    customer_id=789
    product_id="PROD-456"

    # Error information
    error_code="PAYMENT_FAILED"
    error_type="ValidationError"
    error_message="Invalid credit card"

Units in Field Names
~~~~~~~~~~~~~~~~~~~~

Always include units in field names:

.. code-block:: python

    # Good: Units are clear
    logger.info("API response", 
               response_time_ms=250,      # milliseconds
               response_size_bytes=1024,  # bytes
               cache_ttl_seconds=3600)    # seconds

    # Avoid: Ambiguous units
    logger.info("API response", 
               response_time=250,    # ms? seconds?
               response_size=1024,   # bytes? KB?
               cache_ttl=3600)       # seconds? minutes?

Structured Logging Patterns
----------------------------

Event-Based Logging
~~~~~~~~~~~~~~~~~~~

Structure logs around business events:

.. code-block:: python

    # User events
    logger.info("user.login", 
               user_id=123, 
               login_method="password", 
               success=True)

    logger.info("user.logout", 
               user_id=123, 
               session_duration_minutes=45)

    # Order events
    logger.info("order.created", 
               order_id="ORD-123", 
               customer_id=456, 
               total_amount=99.99)

    logger.info("order.payment_processed", 
               order_id="ORD-123", 
               payment_method="credit_card", 
               amount=99.99)

State Transitions
~~~~~~~~~~~~~~~~~

Log important state changes:

.. code-block:: python

    def process_order(order_id):
        logger.info("order.state_changed", 
                   order_id=order_id, 
                   from_state="pending", 
                   to_state="processing")
        
        try:
            # Process order
            logger.info("order.state_changed", 
                       order_id=order_id, 
                       from_state="processing", 
                       to_state="completed")
        except Exception as e:
            logger.error("order.state_changed", 
                        order_id=order_id, 
                        from_state="processing", 
                        to_state="failed",
                        error_reason=str(e))

Performance Monitoring
~~~~~~~~~~~~~~~~~~~~~~

Log performance metrics consistently:

.. code-block:: python

    import time
    from contextlib import contextmanager

    @contextmanager
    def timed_operation(operation_name, **context):
        start_time = time.time()
        
        logger.info(f"{operation_name}.started", **context)
        
        try:
            yield
            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"{operation_name}.completed", 
                       duration_ms=round(duration_ms, 2), 
                       **context)
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"{operation_name}.failed", 
                        duration_ms=round(duration_ms, 2),
                        error_type=type(e).__name__,
                        error_message=str(e),
                        **context)
            raise

    # Usage
    with timed_operation("database.query", table="users", query_type="SELECT"):
        results = db.execute("SELECT * FROM users WHERE active = true")

Error Handling Patterns
------------------------

Structured Error Logging
~~~~~~~~~~~~~~~~~~~~~~~~~

Always include relevant context in error logs:

.. code-block:: python

    def process_payment(user_id, amount, payment_method):
        try:
            # Payment processing logic
            result = payment_gateway.charge(amount, payment_method)
            
            logger.info("payment.successful",
                       user_id=user_id,
                       amount=amount,
                       payment_method=payment_method,
                       transaction_id=result.transaction_id)
            
        except PaymentDeclinedError as e:
            logger.warning("payment.declined",
                          user_id=user_id,
                          amount=amount,
                          payment_method=payment_method,
                          decline_reason=e.reason,
                          decline_code=e.code)
            raise
            
        except PaymentGatewayError as e:
            logger.error("payment.gateway_error",
                        exc_info=True,
                        user_id=user_id,
                        amount=amount,
                        payment_method=payment_method,
                        gateway_error_code=e.error_code,
                        gateway_message=e.message,
                        retry_count=getattr(e, 'retry_count', 0))
            raise
            
        except Exception as e:
            logger.critical("payment.unexpected_error",
                           exc_info=True,
                           user_id=user_id,
                           amount=amount,
                           payment_method=payment_method,
                           error_type=type(e).__name__)
            raise

Error Classification
~~~~~~~~~~~~~~~~~~~~~

Use consistent error classification:

.. code-block:: python

    # Client errors (4xx equivalent)
    logger.warning("validation.failed",
                  field="email",
                  value="invalid-email",
                  error_type="client_error")

    # Server errors (5xx equivalent)
    logger.error("database.connection_failed",
                host="db.example.com",
                error_type="server_error")

    # Business logic errors
    logger.info("business_rule.violated",
               rule="max_daily_transactions",
               user_id=123,
               current_count=10,
               limit=5,
               error_type="business_error")

Context Management Best Practices
----------------------------------

Web Application Context
~~~~~~~~~~~~~~~~~~~~~~~

Set up comprehensive request context:

.. code-block:: python

    def setup_request_context(request):
        """Set up logging context for web requests"""
        context = {
            'request_id': generate_request_id(),
            'method': request.method,
            'path': request.path,
            'ip_address': get_client_ip(request),
            'user_agent': request.headers.get('User-Agent', 'Unknown')[:200]  # Truncate long user agents
        }
        
        # Add user context if authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            context.update({
                'user_id': request.user.id,
                'username': request.user.username,
                'user_role': getattr(request.user, 'role', 'user')
            })
        
        # Add API version if available
        if 'X-API-Version' in request.headers:
            context['api_version'] = request.headers['X-API-Version']
        
        logstructor.bind_context(**context)

Background Task Context
~~~~~~~~~~~~~~~~~~~~~~~

For background tasks, preserve relevant context:

.. code-block:: python

    def enqueue_background_task(task_func, *args, **kwargs):
        """Enqueue background task with current context"""
        current_context = logstructor.get_context()
        
        def wrapped_task():
            # Restore context in background thread
            logstructor.bind_context(**current_context)
            try:
                logger.info("background_task.started", 
                           task_name=task_func.__name__)
                result = task_func(*args, **kwargs)
                logger.info("background_task.completed", 
                           task_name=task_func.__name__)
                return result
            except Exception as e:
                logger.error("background_task.failed",
                            task_name=task_func.__name__,
                            error_type=type(e).__name__,
                            error_message=str(e))
                raise
            finally:
                logstructor.clear_context()
        
        # Queue the wrapped task
        task_queue.enqueue(wrapped_task)

Async Context Management
~~~~~~~~~~~~~~~~~~~~~~~~

For async applications, context is automatically preserved:

.. code-block:: python

    async def handle_async_request():
        logstructor.bind_context(request_id="req-123")
        
        try:
            await authenticate_user()  # Context preserved across await
            logger.info("User authenticated")
            
            await process_data()       # Still has request_id
            logger.info("Processing complete")
            
        finally:
            logstructor.clear_context()

    # Context is isolated between concurrent tasks
    async def main():
        tasks = [handle_async_request() for _ in range(10)]
        await asyncio.gather(*tasks)  # Each task has its own context

Performance Optimization
------------------------

Lazy Evaluation
~~~~~~~~~~~~~~~

Use lazy evaluation for expensive operations:

.. code-block:: python

    # Bad: Always calculates, even if debug is disabled
    logger.debug("User data", user_data=expensive_user_calculation())

    # Good: Only calculate if debug logging is enabled
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("User data", user_data=expensive_user_calculation())

    # Even better: Use a lambda for truly lazy evaluation
    def log_debug_data():
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("User data", user_data=expensive_user_calculation())

Efficient Data Extraction
~~~~~~~~~~~~~~~~~~~~~~~~~~

Extract only what you need for logging:

.. code-block:: python

    # Bad: Serializing entire complex object
    logger.info("User updated", user_object=user)

    # Good: Extract specific fields
    logger.info("User updated",
               user_id=user.id,
               username=user.username,
               email=user.email,
               last_login=user.last_login.isoformat() if user.last_login else None)

Batch Context Updates
~~~~~~~~~~~~~~~~~~~~~

Set context once, not repeatedly:

.. code-block:: python

    # Bad: Setting context multiple times
    for item in items:
        logstructor.bind_context(item_id=item.id)
        logger.info("Processing item")
        logstructor.clear_context()

    # Good: Process in batches or use different approach
    logstructor.bind_context(batch_id="batch-123", total_items=len(items))
    for i, item in enumerate(items):
        logger.info("Processing item", 
                   item_id=item.id, 
                   item_index=i)
    logstructor.clear_context()

Production Deployment
---------------------

Log Level Configuration
~~~~~~~~~~~~~~~~~~~~~~~

Use appropriate log levels in production:

.. code-block:: python

    # Development
    logging.getLogger().setLevel(logging.DEBUG)

    # Staging
    logging.getLogger().setLevel(logging.INFO)

    # Production
    logging.getLogger().setLevel(logging.WARNING)

    # Critical systems
    logging.getLogger().setLevel(logging.ERROR)

Sensitive Data Handling
~~~~~~~~~~~~~~~~~~~~~~~

Never log sensitive information:

.. code-block:: python

    # Bad: Logging sensitive data
    logger.info("User login", 
               username=username, 
               password=password)  # Never log passwords!

    # Good: Log safely
    logger.info("User login", 
               username=username, 
               password_length=len(password),
               has_special_chars=any(c in password for c in "!@#$%"))

    # For debugging, use hashed values
    import hashlib
    password_hash = hashlib.sha256(password.encode()).hexdigest()[:8]
    logger.debug("Login attempt", 
                username=username, 
                password_hash=password_hash)

Data Sanitization
~~~~~~~~~~~~~~~~~

Sanitize user input in logs:

.. code-block:: python

    def sanitize_for_logging(value, max_length=200):
        """Sanitize user input for safe logging"""
        if value is None:
            return None
        
        # Convert to string and truncate
        str_value = str(value)[:max_length]
        
        # Remove potentially dangerous characters
        safe_value = ''.join(c for c in str_value if c.isprintable())
        
        return safe_value

    # Usage
    logger.info("User input received", 
               user_input=sanitize_for_logging(user_input),
               input_length=len(user_input))

Monitoring and Alerting
-----------------------

Health Check Logging
~~~~~~~~~~~~~~~~~~~~

Log application health metrics:

.. code-block:: python

    def log_health_metrics():
        """Log application health metrics"""
        import psutil
        import gc
        
        logger.info("health.metrics",
                   cpu_percent=psutil.cpu_percent(),
                   memory_percent=psutil.virtual_memory().percent,
                   disk_usage_percent=psutil.disk_usage('/').percent,
                   active_connections=len(psutil.net_connections()),
                   gc_collections=sum(gc.get_stats(), []).get('collections', 0))

    # Call periodically
    import threading
    import time

    def health_monitor():
        while True:
            log_health_metrics()
            time.sleep(60)  # Every minute

    health_thread = threading.Thread(target=health_monitor, daemon=True)
    health_thread.start()

Business Metrics
~~~~~~~~~~~~~~~~

Log business-relevant metrics:

.. code-block:: python

    def log_business_metrics():
        """Log business metrics for monitoring"""
        logger.info("business.metrics",
                   active_users_count=get_active_users_count(),
                   orders_today=get_orders_count_today(),
                   revenue_today=get_revenue_today(),
                   error_rate_percent=get_error_rate_last_hour(),
                   avg_response_time_ms=get_avg_response_time())

Alert-Worthy Events
~~~~~~~~~~~~~~~~~~~

Structure logs for easy alerting:

.. code-block:: python

    # High-priority alerts
    logger.critical("system.critical_error",
                    error_type="database_unavailable",
                    affected_users="all",
                    estimated_downtime_minutes=5)

    # Medium-priority alerts
    logger.error("business.threshold_exceeded",
                metric="error_rate",
                current_value=15.5,
                threshold=10.0,
                time_window_minutes=5)

    # Low-priority alerts
    logger.warning("system.resource_warning",
                  resource="memory",
                  current_usage_percent=85,
                  threshold_percent=80)

Testing Structured Logs
------------------------

Log Testing Utilities
~~~~~~~~~~~~~~~~~~~~~

Create utilities for testing log output:

.. code-block:: python

    import json
    from io import StringIO
    import logging

    class LogCapture:
        """Utility for capturing and testing log output"""
        
        def __init__(self):
            self.stream = StringIO()
            self.handler = logging.StreamHandler(self.stream)
            self.handler.setFormatter(logstructor.StructFormatter())
            
        def __enter__(self):
            logger = logstructor.getLogger("test")
            logger.addHandler(self.handler)
            logger.setLevel(logging.DEBUG)
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            logger = logstructor.getLogger("test")
            logger.removeHandler(self.handler)
            
        def get_logs(self):
            """Get all captured logs as parsed JSON objects"""
            logs = []
            for line in self.stream.getvalue().strip().split('\n'):
                if line:
                    logs.append(json.loads(line))
            return logs
        
        def assert_log_contains(self, level, message, **expected_context):
            """Assert that a log entry exists with expected content"""
            logs = self.get_logs()
            
            for log in logs:
                if (log.get('level') == level and 
                    log.get('message') == message):
                    
                    # Check context fields
                    context = log.get('context', {})
                    for key, value in expected_context.items():
                        if context.get(key) != value:
                            break
                    else:
                        return True
            
            raise AssertionError(f"Expected log not found: {level} {message} {expected_context}")

    # Usage in tests
    def test_user_login_logging():
        with LogCapture() as capture:
            logger = logstructor.getLogger("test")
            logger.info("User logged in", user_id=123, method="password")
            
            capture.assert_log_contains("INFO", "User logged in", 
                                       user_id=123, method="password")

Integration Testing
~~~~~~~~~~~~~~~~~~~

Test log output in integration tests:

.. code-block:: python

    def test_api_request_logging(client):
        """Test that API requests are properly logged"""
        with LogCapture() as capture:
            response = client.get('/api/users/123')
            
            logs = capture.get_logs()
            
            # Check request started log
            request_logs = [log for log in logs if "Request started" in log.get('message', '')]
            assert len(request_logs) == 1
            assert request_logs[0]['context']['method'] == 'GET'
            assert request_logs[0]['context']['path'] == '/api/users/123'
            
            # Check request completed log
            completion_logs = [log for log in logs if "Request completed" in log.get('message', '')]
            assert len(completion_logs) == 1
            assert completion_logs[0]['context']['status_code'] == 200

Common Anti-Patterns
--------------------

Avoid These Mistakes
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # ❌ Don't log sensitive data
    logger.info("User login", password=password, credit_card=card_number)

    # ❌ Don't use inconsistent field names
    logger.info("Event", userId=123)  # camelCase
    logger.info("Event", user_id=123)  # snake_case (pick one!)

    # ❌ Don't forget to clear context
    logstructor.bind_context(request_id="req-123")
    # ... process request ...
    # Context never cleared - memory leak!

    # ❌ Don't log complex objects directly
    logger.info("User data", user=complex_user_object)  # Hard to search

    # ❌ Don't use vague messages
    logger.info("Something happened", data=some_data)  # Not helpful

    # ❌ Don't ignore performance
    logger.debug("Debug info", expensive_data=slow_calculation())  # Always calculated

Better Alternatives
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # ✅ Log safely
    logger.info("User login", username=username, login_successful=True)

    # ✅ Use consistent naming
    logger.info("Event", user_id=123)  # Always snake_case

    # ✅ Always clear context
    try:
        logstructor.bind_context(request_id="req-123")
        # ... process request ...
    finally:
        logstructor.clear_context()

    # ✅ Extract relevant fields
    logger.info("User data", user_id=user.id, username=user.username)

    # ✅ Use descriptive messages
    logger.info("User authentication successful", user_id=123, method="password")

    # ✅ Use lazy evaluation
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Debug info", expensive_data=slow_calculation())

Next Steps
----------

- :doc:`context-management` - Advanced context management
- :doc:`json-formatting` - JSON formatting configuration