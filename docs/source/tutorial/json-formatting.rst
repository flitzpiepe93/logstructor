JSON Formatting
===============

LogStructor automatically configures structured JSON output - no manual setup required! This makes your logs immediately searchable and analyzable by log aggregation systems.

Automatic JSON Output
---------------------

Simply use ``logstructor.getLogger()`` and your logs are automatically JSON:

.. code-block:: python

    import logstructor

    # LogStructor automatically configures JSON formatting
    logger = logstructor.getLogger(__name__)

    # Your logs are automatically structured JSON
    logger.info("User logged in", user_id=123, ip="192.168.1.100")

**Output:**

.. code-block:: json

    {
      "timestamp": "2025-01-08T10:30:45Z",
      "level": "INFO",
      "logger": "__main__",
      "message": "User logged in",
      "context": {
        "user_id": 123,
        "ip": "192.168.1.100"
      }
    }

Custom Configuration (Optional)
-------------------------------

If you need custom settings, use ``logstructor.configure()``:

.. code-block:: python

    import logstructor

    # Optional: Custom configuration before creating loggers
    logstructor.configure(
        level="DEBUG",
        timestamp_format="epoch",
        extra_fields={
            "service": "user-api",
            "version": "1.2.3"
        }
    )

    # Now all loggers use your custom configuration
    logger = logstructor.getLogger(__name__)
    logger.info("Custom configured log", user_id=123)

JSON Structure
--------------

Every JSON log entry has this consistent structure:

Standard Fields
~~~~~~~~~~~~~~~

- **timestamp**: ISO 8601 timestamp or Unix epoch
- **level**: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **logger**: Logger name
- **message**: Human-readable log message

Context Field
~~~~~~~~~~~~~

- **context**: Object containing all structured fields

.. code-block:: json

    {
      "timestamp": "2025-01-08T10:30:45Z",
      "level": "ERROR",
      "logger": "payment_service",
      "message": "Payment processing failed",
      "context": {
        "user_id": 123,
        "transaction_id": "txn_789",
        "amount": 99.99,
        "error_code": "INSUFFICIENT_FUNDS"
      }
    }

Formatter Configuration
-----------------------

Timestamp Formats
~~~~~~~~~~~~~~~~~

Choose between ISO 8601 and Unix epoch timestamps:

.. code-block:: python

    from logstructor import StructFormatter

    # ISO 8601 format (default)
    iso_formatter = StructFormatter(timestamp_format="iso")
    # Output: "2025-01-08T10:30:45Z"

    # Unix epoch format
    epoch_formatter = StructFormatter(timestamp_format="epoch")
    # Output: 1704715845.123

Static Extra Fields
~~~~~~~~~~~~~~~~~~~

Add static fields to every log entry:

.. code-block:: python

    formatter = StructFormatter(extra_fields={
        "service": "user-api",
        "version": "1.2.3",
        "environment": "production",
        "datacenter": "us-east-1"
    })

    logger.info("Request processed", user_id=123)

**Output:**

.. code-block:: json

    {
      "timestamp": "2025-01-08T10:30:45Z",
      "level": "INFO",
      "logger": "__main__",
      "message": "Request processed",
      "context": {
        "service": "user-api",
        "version": "1.2.3",
        "environment": "production",
        "datacenter": "us-east-1",
        "user_id": 123
      }
    }

Context Field Behavior
----------------------

When Context is Included
~~~~~~~~~~~~~~~~~~~~~~~~

The ``context`` field appears when there are structured fields to include:

.. code-block:: python

    # No context field (no structured data)
    logger.info("Simple message")
    # → {"timestamp": "...", "level": "INFO", "message": "Simple message"}

    # Context field included
    logger.info("User action", user_id=123)
    # → {"timestamp": "...", "level": "INFO", "message": "User action", "context": {"user_id": 123}}

Context Sources
~~~~~~~~~~~~~~~

The context field combines data from multiple sources:

1. **Context data** (from ``bind_context()``)
2. **Static extra fields** (from formatter configuration)
3. **Structured fields** (from log call keyword arguments)

.. code-block:: python

    # Set up static fields
    formatter = StructFormatter(extra_fields={"service": "api"})

    # Set context data
    logstructor.bind_context(request_id="req-123")

    # Log with structured fields
    logger.info("Processing", user_id=456, action="login")

**Output:**

.. code-block:: json

    {
      "timestamp": "2025-01-08T10:30:45Z",
      "level": "INFO",
      "logger": "__main__",
      "message": "Processing",
      "context": {
        "service": "api",        
        "request_id": "req-123", 
        "user_id": 456,         
        "action": "login"       
      }
    }

Data Type Handling
------------------

LogStructor automatically serializes Python data types to JSON:

Basic Types
~~~~~~~~~~~

.. code-block:: python

    logger.info("Data types",
               string_val="hello",
               int_val=42,
               float_val=3.14,
               bool_val=True,
               null_val=None)

**Output:**

.. code-block:: json

    {
      "context": {
        "string_val": "hello",
        "int_val": 42,
        "float_val": 3.14,
        "bool_val": true,
        "null_val": null
      }
    }

Complex Types
~~~~~~~~~~~~~

.. code-block:: python

    from datetime import datetime

    logger.info("Complex types",
               timestamp=datetime.now(),
               list_data=[1, 2, "three"],
               dict_data={"nested": {"key": "value"}})

**Output:**

.. code-block:: json

    {
      "context": {
        "timestamp": "2025-01-08T10:30:45.123456",
        "list_data": [1, 2, "three"],
        "dict_data": {
          "nested": {
            "key": "value"
          }
        }
      }
    }

Custom Objects
~~~~~~~~~~~~~~

Objects are converted using their string representation:

.. code-block:: python

    class User:
        def __init__(self, id, name):
            self.id = id
            self.name = name
        
        def __str__(self):
            return f"User(id={self.id}, name={self.name})"

    user = User(123, "alice")
    logger.info("User created", user_obj=user)

**Output:**

.. code-block:: json

    {
      "context": {
        "user_obj": "User(id=123, name=alice)"
      }
    }

Multiple Handlers
-----------------

Use different formatters for different outputs:

.. code-block:: python

    import logging
    from logstructor import StructFormatter

    logger = logstructor.getLogger(__name__)

    # Console handler with human-readable format
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    # File handler with JSON format
    file_handler = logging.FileHandler('app.log')
    json_formatter = StructFormatter()
    file_handler.setFormatter(json_formatter)

    # Add both handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # This log goes to both console (human-readable) and file (JSON)
    logger.info("Application started", version="1.0.0", port=8080)

Log Aggregator Integration
---------------------------

ELK Stack (Elasticsearch, Logstash, Kibana)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configure Logstash to parse LogStructor JSON:

.. code-block:: ruby

    # logstash.conf
    input {
      file {
        path => "/var/log/app.log"
        codec => "json"
      }
    }

    filter {
      # LogStructor logs are already structured
      # No additional parsing needed
    }

    output {
      elasticsearch {
        hosts => ["localhost:9200"]
        index => "app-logs-%{+YYYY.MM.dd}"
      }
    }

Query in Kibana:

.. code-block:: text

    context.user_id:123
    level:ERROR
    context.response_time_ms:>1000

Splunk
~~~~~~

LogStructor JSON works directly with Splunk:

.. code-block:: text

    # Search for user actions
    index=app_logs context.user_id=123

    # Find slow requests
    index=app_logs context.response_time_ms>1000

    # Error analysis
    index=app_logs level=ERROR | stats count by context.error_code

Datadog
~~~~~~~

Configure Datadog agent to parse JSON logs:

.. code-block:: yaml

    # datadog.yaml
    logs:
      - type: file
        path: /var/log/app.log
        service: my-app
        source: python
        sourcecategory: sourcecode

Query in Datadog:

.. code-block:: text

    @context.user_id:123
    @level:ERROR
    @context.response_time_ms:>1000

Performance Considerations
--------------------------

JSON Serialization Overhead
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

JSON formatting adds minimal overhead:

.. code-block:: python

    # Benchmark results (approximate)
    # Standard logging:  100,000 msgs/sec
    # LogStructor JSON:   85,000 msgs/sec
    # Overhead: ~15%

Optimization Tips
~~~~~~~~~~~~~~~~~

1. **Use simple data types** when possible:

.. code-block:: python

    # Faster
    logger.info("User action", user_id=123, action="login")

    # Slower (complex object serialization)
    logger.info("User action", user_object=complex_user_object)

2. **Avoid deep nesting**:

.. code-block:: python

    # Better
    logger.info("Order", order_id=order.id, customer_id=order.customer_id)

    # Avoid
    logger.info("Order", order_data=order.to_dict())  # If deeply nested

3. **Use appropriate log levels**:

.. code-block:: python

    # Only serialize debug data when needed
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Debug info", expensive_data=calculate_debug_data())

Unicode and Special Characters
------------------------------

LogStructor handles Unicode correctly:

.. code-block:: python

    logger.info("International user", 
               username="José María", 
               message="Hello 世界 🌍",
               emoji_reaction="👍")

**Output:**

.. code-block:: json

    {
      "context": {
        "username": "José María",
        "message": "Hello 世界 🌍",
        "emoji_reaction": "👍"
      }
    }

Error Handling
--------------

The formatter handles serialization errors gracefully:

.. code-block:: python

    class UnserializableObject:
        def __init__(self):
            self.file_handle = open("somefile.txt")

    # This won't crash - uses str() fallback
    logger.info("Problematic object", obj=UnserializableObject())

Custom Formatter Example
-------------------------

Create a custom formatter for specific needs:

.. code-block:: python

    import json
    import logging
    from datetime import datetime, timezone
    from logstructor import StructFormatter

    class CustomStructFormatter(StructFormatter):
        """Custom formatter with additional fields"""
        
        def format(self, record):
            # Get the base JSON structure
            log_entry = json.loads(super().format(record))
            
            # Add custom fields
            log_entry["hostname"] = "server-01"
            log_entry["environment"] = "production"
            log_entry["version"] = "1.2.3"
            
            # Custom timestamp format
            log_entry["@timestamp"] = datetime.now(timezone.utc).isoformat()
            
            return json.dumps(log_entry, ensure_ascii=False)

    # Use custom formatter
    handler = logging.StreamHandler()
    handler.setFormatter(CustomStructFormatter())
    logger.addHandler(handler)

Next Steps
----------

- :doc:`context-management` - Learn about context management
- :doc:`best-practices` - Production deployment patterns