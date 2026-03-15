# logbook-stubs

Type stubs for [Logbook](https://pypi.org/project/Logbook/).

Provides `.pyi` files for type checking and IDE autocompletion.

## Installation

```bash
pip install logbook-stubs
```

or

```sh
uv add logbook-stubs --group test
```

## Usage

Type checkers use these stubs automatically when you `import logbook`.

Example:

```py
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logbook.base import LogRecord


def emit(record: LogRecord) ->  None:
    ...
```

## Included

- `logbook.base`: `LogRecord`, levels
- `logbook.handlers`: Handlers, formatters

## Compatibility

Tested with Logbook >= 1.9.0. It does not cover all classes in Logbook yet.
