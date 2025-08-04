# Contributing to LogStructor

Thank you for your interest in contributing to LogStructor! We welcome contributions from the community and are excited to see what you'll bring to the project.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) for dependency management (recommended)
- Git

### Setting Up Your Development Environment

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/your-username/logstructor.git
   cd logstructor
   ```

2. **Install dependencies using uv:**
   ```bash
   uv sync --all-groups
   ```

   Or if you prefer pip:
   ```bash
   pip install -e ".[test,linting,docs]"
   ```

3. **Verify your setup:**
   ```bash
   uv run pytest
   uv run ruff check
   uv run mypy logstructor
   ```

## Development Workflow

### Code Style and Quality

We maintain high code quality standards using automated tools:

- **Ruff** for linting and formatting
- **MyPy** for type checking
- **Pytest** for testing

Before submitting any changes, ensure your code passes all checks:

```bash
# Format code
uv run ruff format

# Check linting
uv run ruff check

# Type checking
uv run mypy logstructor

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=logstructor --cov-report=html
```

### Running Tests

We have comprehensive test coverage. Run the full test suite:

```bash
# All tests
uv run pytest

# Specific test file
uv run pytest tests/test_logger.py

# With coverage report
uv run pytest --cov=logstructor --cov-report=term-missing

# Async tests only
uv run pytest -k "async"
```

### Documentation

Documentation is built with Sphinx and hosted as part of the project:

```bash
# Build documentation
cd docs
uv run sphinx-build -b html source build

# Serve locally (if you have a simple HTTP server)
cd build && python -m http.server 8000
```

## Contributing Guidelines

### Types of Contributions

We welcome several types of contributions:

- **Bug fixes** - Fix issues in existing functionality
- **Feature enhancements** - Improve existing features
- **New features** - Add new functionality (please discuss first)
- **Documentation** - Improve docs, examples, or tutorials
- **Tests** - Add or improve test coverage
- **Performance** - Optimize existing code

### Before You Start

For significant changes, please:

1. **Open an issue** to discuss your proposed changes
2. **Check existing issues** to avoid duplicate work
3. **Review the roadmap** to align with project direction

### Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards

3. **Add tests** for any new functionality

4. **Update documentation** if needed

5. **Ensure all checks pass:**
   ```bash
   uv run ruff check
   uv run mypy logstructor
   uv run pytest
   ```

### Commit Messages

We use conventional commits for automated changelog generation:

```
feat: add support for custom timestamp formats
fix: resolve context isolation issue in async functions
docs: improve context management examples
test: add tests for thread safety
refactor: simplify formatter initialization
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `ci`, `chore`

### Pull Request Process

1. **Ensure your branch is up to date:**
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-branch
   git rebase main
   ```

2. **Create a pull request** with:
   - Clear title and description
   - Reference to related issues
   - Summary of changes made
   - Any breaking changes noted

3. **Respond to feedback** promptly and make requested changes

4. **Ensure CI passes** - all automated checks must pass

## Code Standards

### Python Code Style

- Follow PEP 8 (enforced by Ruff)
- Use type hints for all public APIs
- Write comprehensive docstrings with examples
- Keep functions focused and testable
- Prefer composition over inheritance

### Example of Good Code Style

```python
def bind_context(**kwargs: Any) -> None:
    """
    Bind key-value pairs to the current context's logging context.

    These fields will be automatically included in all subsequent log entries
    within the current context until cleared or overwritten.

    Args:
        **kwargs: Key-value pairs to bind to the context

    Examples:
        Basic usage:
        >>> bind_context(request_id="req-123", user_id=456)
        >>> logger.info("Processing request")  # Will include request_id and user_id

        Web application example:
        >>> bind_context(request_id=request.id, user_id=request.user.id)
        >>> logger.info("User login attempt")  # Automatically includes context
    """
    current_context = _context_data.get().copy()
    current_context.update(kwargs)
    _context_data.set(current_context)
```

### Testing Standards

- Write tests for all new functionality
- Aim for high test coverage (>90%)
- Include both positive and negative test cases
- Test async functionality where applicable
- Use descriptive test names

```python
def test_bind_context_overwrites_existing():
    """Test that bind_context overwrites existing keys."""
    bind_context(user_id=123)
    bind_context(user_id=456)  # Should overwrite

    context = get_context()
    assert context["user_id"] == 456
```

## Project Structure

```
logstructor/
├── logstructor/           # Main package
│   ├── __init__.py       # Public API
│   ├── logger.py         # StructLogger implementation
│   ├── formatter.py      # JSON formatter
│   ├── context.py        # Context management
│   ├── config.py         # Configuration utilities
│   └── exceptions.py     # Custom exceptions
├── tests/                # Test suite
├── docs/                 # Sphinx documentation
├── examples/             # Usage examples
└── pyproject.toml        # Project configuration
```

## Design Principles

1. **Backward Compatibility** - Never break existing logging code
2. **Zero Dependencies** - Keep the core lightweight
3. **Thread Safety** - Support multi-threaded applications
4. **Async Support** - First-class async/await support
5. **Performance** - Minimal overhead over standard logging
6. **Simplicity** - Easy to use, hard to misuse

## Release Process

Releases are automated using semantic-release:

1. Merge changes to `main` branch
2. Semantic-release analyzes commit messages
3. Version is bumped automatically
4. Changelog is generated
5. Package is published to PyPI

## Getting Help

- **Issues**: Open a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check the docs at `docs/`

## Recognition

Contributors are recognized in:
- GitHub contributors list
- Release notes for significant contributions
- Documentation acknowledgments

Thank you for contributing to LogStructor! 🚀