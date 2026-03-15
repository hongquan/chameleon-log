# AGENTS.md

Guide for AI agents working in this codebase.

## Project Overview

**ChameleonLog** is a Python library providing a Rich-based colourful handler for [Logbook](https://pypi.org/project/Logbook/). It enables colourful, formatted log output using the [Rich](https://pypi.org/project/rich/) library.

## Commands

### Package Management

Uses `uv` for dependency management (uv.lock present).

```bash
# Install dependencies
uv sync

# Install with dev dependencies
uv sync --group dev --group lint --group test

# Add a dependency
uv add <package>

# Add a dev dependency
uv add --group dev <package>
```

### Building

```bash
# Build the package
uv build
```

### Documentation

Use Sphinx to build documentation.

```bash
# Install dependencies including all optional extras (required for building docs)
uv sync --group docs --all-extras

# Build HTML documentation
cd docs && make html

# Auto-rebuild and serve documentation
cd docs && make livehtml
```

**Note**: Building documentation requires the `--all-extras` flag to ensure the `journald` module is available for autodoc generation, even though it uses a no-op implementation if systemd-python is not installed.

### Linting & Formatting

Uses Ruff for both linting and formatting.

```bash
# Run linter
uv run ruff check

# Format code
uv run ruff format

# Check formatting without changes
uv run ruff format --check
```

### Type Checking

Uses `ty` for type checking.

```bash
uv run ty check src/
```

### Testing

Tests use the `ty` library (in test dependency group).

```bash
uv run pytest
# or if using ty directly:
uv run ty test
```

## Workspace Layout

This project uses `uv` workspace with two members:

```
chameleon-log/                   # Root workspace
├── src/
│   └── chameleon_log/           # Main package
│       ├── __init__.py          # Version definition
│       ├── rich.py              # RichHandler implementation
│       └── py.typed             # PEP 561 marker for type hints
├── packages/
│   └── logbook-stubs/           # Workspace member: stub-only package
│       ├── pyproject.toml
│       └── logbook/             # PEP 561 stub package directory
│           ├── __init__.pyi
│           ├── base.pyi         # LogRecord, Logger, level constants
│           ├── handlers.pyi     # Handler, StderrHandler, Formatter stubs
│           └── py.typed         # PEP 561 marker for type stubs
├── examples/                    # Example usage (currently empty)
├── pyproject.toml               # Root project config, tool settings
└── uv.lock                      # Workspace lockfile
```

The `logbook-stubs` package provides type stubs for the `logbook` library since it lacks type hints.

## Code Conventions

### Python Version

- Requires Python >= 3.12
- Uses modern Python syntax (e.g., `type` alias syntax in handlers.py:14)

### Type Hints

- **Strict mypy mode is enabled** - all functions must have complete type annotations
- The project ships type hints (py.typed marker present)
- Stub files (.pyi) are provided for the logbook dependency since it lacks type hints
- Use `from __future__ import annotations` if needed for forward references

### Ruff Configuration

- Line length: 120 characters
- Quote style: single quotes (`'`)
- Enabled rules: E4, E7, E9, F, I, BLE001, ANN
- Isort: 2 blank lines after imports

Example:
```python
from typing import Literal

from rich import get_console


def example() -> None:
    pass
```

### Import Style

- Two blank lines after imports (configured in ruff.lint.isort)
- Absolute imports from the project: prefer `from logbook_rich.handlers import RichHandler`
- External imports grouped before local imports

## Architecture Notes

### Type Completeness

The library strives for type completeness. Since `logbook` lacks type hints, stub files are provided in `packages/logbook-stubs/logbook-stubs/`. These stubs define only what's needed:

- `base.pyi`: Level constants (CRITICAL=15, ERROR=14, etc.), NOTSET=0, LogRecord class
- `handlers.pyi`: Handler, StreamHandler, StderrHandler, Formatter classes with method signatures


### RichHandler

The main class in `handlers.py`. Extends `StderrHandler` from logbook and uses Rich's `LogRender` for formatted output.

Key attributes mirror Rich's logging capabilities:
- `show_time`, `show_level`, `show_path` - display toggles
- `tracebacks_*` - traceback configuration options
- `markup` - enable Rich markup in messages

## Gotchas

1. **Unused import warning**: `rich.logging.RichHandler` is imported but unused in handlers.py. This may be intentional for future use or should be removed.

2. **Logbook stubs are minimal**: The stub files in `packages/logbook-stubs/logbook/` only define what this project needs. If you need additional logbook types, add them to the stubs.

3. **Version is in `__init__.py`**: The `__version__` variable is read by hatchling for dynamic versioning:
   ```python
   __version__ = '0.1.0'
   ```

4. **No tests yet**: The examples/ directory is empty and there are no test files. When adding tests, place them in a `tests/` directory or alongside source files.

5. **JournaldHandler is optional**: The `JournaldHandler` is only functional when the `journald` extra is installed. Without it, the handler is available but acts as a no-op (does nothing). This allows code to optionally use journald logging without crashing if the dependency is missing.

## Dependencies

### Runtime
- `logbook>=1.9.0`
- `rich>=14.1.0`

### Dev (dependency groups)
- `test`: ty>=0.0.23
- `lint`: ruff>=0.12.5
- `dev`: pre-commit>=4.2.0
- `docs`: sphinx, sphinx-autobuild, sphinx-book-theme, myst-parser, sphinxcontrib-asciinema

**Note**: When building documentation, use `uv sync --group docs --all-extras` to ensure optional dependencies like `journald` are available for autodoc.
