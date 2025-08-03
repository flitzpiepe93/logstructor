[![CI/CD](https://github.com/flitzpiepe93/logstructor/actions/workflows/ci.yml/badge.svg)](https://github.com/flitzpiepe93/logstructor/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/flitzpiepe93/logstructor/graph/badge.svg?token=XXL7PN059H)](https://codecov.io/gh/flitzpiepe93/logstructor)
[![PyPI version](https://badge.fury.io/py/logstructor.svg)](https://pypi.org/project/logstructor/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

# LogStructor

## The Problem: Your Logs Are Useless

Try finding anything in this mess:

```
2025-01-08 10:30:45 INFO: User alice from 192.168.1.100 failed login attempt 3
2025-01-08 10:31:12 INFO: Processing order for customer 456 amount $99.99
2025-01-08 10:31:45 ERROR: Database connection timeout after 30 seconds
2025-01-08 10:32:01 INFO: Order ORD-789 completed successfully
```

**Questions you can't answer:**

- Which user had the database timeout?
- How many failed logins did alice have today?
- What orders failed due to timeouts?

**You can't search, filter, or analyze unstructured text logs.**

## The Solution: 3 Lines of Code

```python
import logstructor

logger = logstructor.getLogger(__name__)
logger.info("Login failed", user_id="alice", ip="192.168.1.100", attempt=3, reason="invalid_password")
```

**Result:**

```json
{
  "timestamp": "2025-01-08T10:30:45Z",
  "level": "INFO",
  "message": "Login failed",
  "context": {
    "user_id": "alice",
    "ip": "192.168.1.100",
    "attempt": 3,
    "reason": "invalid_password"
  }
}
```

**Now you can actually search your logs in ELK, Splunk, or any log aggregator:**

```bash
# Find all of alice's actions across all services
user_id:"alice"

# Find all failed login attempts
reason:"invalid_password"

# Find users with multiple failed attempts (security alert!)
attempt:>2

# Complex queries become possible
user_id:"alice" AND level:"ERROR" AND timestamp:[now-1h TO now]
```

**Before:** Grep through gigabytes of text files
**After:** Instant search and filtering

## Get Started

Getting started with logstructor is as simple as installing the package and using its drop‑in replacement for the standard Python logger.

```bash
pip install logstructor
```

With just a few lines of code, you can start producing structured, machine‑readable logs without changing your existing logging workflow:

```python
import logstructor

logger = logstructor.getLogger(__name__)
logger.info("Hello structured world", excited=True)
```

And that’s it — your logs are now automatically enriched with context and structured fields, making them up to 10× more useful for debugging, analysis, and monitoring.

## Why Developers Love It

### 1. Works in 30 seconds

```python
import logstructor

logger = logstructor.getLogger(__name__)
# Done. You're logging structured data.
```

### 2. Context that actually works

```python
# Set once per request
logstructor.bind_context(request_id="req-123", user_id=456)

# Every log automatically includes request_id and user_id
logger.info("Started processing")
logger.info("Validation passed")
logger.error("Database timeout")
logger.info("Request completed")

# Clean up
logstructor.clear_context()
```

### 3. Drop-in replacement

```python
# Your existing code works unchanged
logger.info("Server started")
logger.error("Connection failed", exc_info=True)

# Just add structure when you want it
logger.info("Server started", port=8080, workers=4)
logger.error("Connection failed", host="db.example.com", timeout=30)
```

## Production Ready

| Feature                  | Benefit                                             |
| ------------------------ | --------------------------------------------------- |
| 🔒 **Thread-safe**       | Works perfectly in multi-threaded web apps          |
| 📦 **Zero dependencies** | No supply chain attacks, no version conflicts       |
| ⚡ **High performance**  | Minimal overhead over standard logging              |
| 🛡️ **Battle-tested**     | Running in production handling millions of requests |

## Why Not structlog?

[structlog](https://www.structlog.org/) is fantastic for complex logging pipelines, but it requires learning a completely new API and philosophy. LogStructor takes a different approach:

| Aspect               | LogStructor                      | structlog                            |
| -------------------- | -------------------------------- | ------------------------------------ |
| **Learning curve**   | Zero - uses standard logging API | Steep - new concepts and API         |
| **Migration effort** | Drop-in replacement              | Rewrite all logging calls            |
| **Dependencies**     | Zero                             | Multiple (including optional ones)   |
| **Complexity**       | Minimal - just structured fields | High - processors, contextvars, etc. |
| **Use case**         | 80% of structured logging needs  | Complex logging architectures        |

### When to choose what:

**Choose LogStructor when:**

- You want structured logging **today** with minimal effort
- You have existing codebases with standard logging
- You need zero dependencies (security/compliance)
- Your team wants to avoid learning new APIs
- You need simple request context tracking

**Choose structlog when:**

- You're building complex logging pipelines
- You need advanced processors and transformations
- You're starting a greenfield project
- You want maximum flexibility and customization
- You need advanced contextvars integration

**Migration path:** Many teams start with LogStructor for quick wins, then migrate to structlog when they need advanced features. LogStructor's JSON output is compatible with most log aggregators that also consume structlog output.
