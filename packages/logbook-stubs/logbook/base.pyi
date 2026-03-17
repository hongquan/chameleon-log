from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from types import FrameType, TracebackType
from typing import TYPE_CHECKING, Callable, Literal, Self, TypeAlias

if TYPE_CHECKING:
    from logbook.handlers import Handler

from _typeshed import Incomplete

StringLevel: TypeAlias = Literal['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTICE', 'TRACE', 'NOTSET']
# Need to keep in sync with the constansts from logbook.base
NumericLevel: TypeAlias = Literal[15, 14, 13, 12, 11, 10, 9, 0]
LogLevel: TypeAlias = StringLevel | NumericLevel

# Type for log filter functions
LogFilter: TypeAlias = Callable[[LogRecord, Handler], bool]

# Level constants
CRITICAL: Literal[15] = 15
ERROR: Literal[14] = 14
WARNING: Literal[13] = 13
INFO: Literal[12] = 12
DEBUG: Literal[11] = 11
NOTICE: Literal[10] = 10
TRACE: Literal[9] = 9
NOTSET: Literal[0] = 0

_ExcInfo = tuple[type[BaseException], BaseException, TracebackType] | tuple[None, None, None]

class LogRecord:
    channel: str
    msg: str
    args: tuple[Incomplete, ...]
    kwargs: dict[str, Incomplete]
    level: LogLevel
    exc_info: _ExcInfo | Literal[True] | None
    extra: defaultdict[str, Incomplete]
    frame: FrameType | None
    frame_correction: int
    process: int | None
    time: datetime | None
    keep_open: bool
    heavy_initialized: bool
    late: bool
    information_pulled: bool

    def __init__(
        self,
        channel: str,
        level: int | StringLevel,
        msg: str,
        args: tuple[Incomplete, ...] | None = ...,
        kwargs: dict[str, Incomplete] | None = ...,
        exc_info: _ExcInfo | Literal[True] | BaseException | None = ...,
        extra: dict[str, Incomplete] | None = ...,
        frame: FrameType | None = ...,
        dispatcher: Incomplete = ...,
        frame_correction: int = ...,
    ) -> None: ...
    @property
    def message(self) -> str: ...
    @property
    def level_name(self) -> str: ...
    @property
    def calling_frame(self) -> FrameType | None: ...
    @property
    def func_name(self) -> str | None: ...
    @property
    def module(self) -> str | None: ...
    @property
    def filename(self) -> str | None: ...
    @property
    def lineno(self) -> int | None: ...
    @property
    def greenlet(self) -> int | None: ...
    @property
    def thread(self) -> int | None: ...
    @property
    def thread_name(self) -> str | None: ...
    @property
    def process_name(self) -> str | None: ...
    @property
    def formatted_exception(self) -> str | None: ...
    @property
    def exception_name(self) -> str | None: ...
    @property
    def exception_shortname(self) -> str | None: ...
    @property
    def exception_message(self) -> str | None: ...
    @property
    def dispatcher(self) -> Incomplete: ...
    def heavy_init(self) -> None: ...
    def pull_information(self) -> None: ...
    def close(self) -> None: ...
    def to_dict(self, json_safe: bool = ...) -> dict[str, Incomplete]: ...
    @classmethod
    def from_dict(cls, d: dict[str, Incomplete]) -> LogRecord: ...
    def update_from_dict(self, d: dict[str, Incomplete]) -> LogRecord: ...

class RecordDispatcher:
    """A record dispatcher is the internal base class that implements
    the logic used by the :class:`~logbook.Logger`.
    """

    suppress_dispatcher: bool
    name: str | None
    handlers: list['Handler']
    group: LoggerGroup | None
    level: int
    disabled: bool

    def __init__(self, name: str | None = None, level: int = ...) -> None: ...
    def handle(self, record: LogRecord) -> None: ...
    def make_record_and_handle(
        self,
        level: int,
        msg: str,
        args: tuple[Incomplete, ...],
        kwargs: dict[str, Incomplete],
        exc_info: _ExcInfo | Literal[True] | BaseException | None,
        extra: dict[str, Incomplete] | None,
        frame_correction: int,
    ) -> None: ...
    def call_handlers(self, record: LogRecord) -> None: ...

class LoggerMixin:
    """This mixin class defines and implements the "usual" logger
    interface (i.e. the descriptive logging functions).
    """

    level_name: str

    def trace(self, *args: Incomplete, **kwargs: Incomplete) -> None: ...
    def debug(self, *args: Incomplete, **kwargs: Incomplete) -> None: ...
    def info(self, *args: Incomplete, **kwargs: Incomplete) -> None: ...
    def notice(self, *args: Incomplete, **kwargs: Incomplete) -> None: ...
    def warning(self, *args: Incomplete, **kwargs: Incomplete) -> None: ...
    def error(self, *args: Incomplete, **kwargs: Incomplete) -> None: ...
    def critical(self, *args: Incomplete, **kwargs: Incomplete) -> None: ...
    def exception(self, *args: Incomplete, **kwargs: Incomplete) -> None: ...
    def log(self, level: int, *args: Incomplete, **kwargs: Incomplete) -> None: ...

class Logger(RecordDispatcher, LoggerMixin):
    """Instances of the Logger class represent a single logging channel."""

    def __init__(self, name: str | None = None, level: int = ...) -> None: ...

class LoggerGroup:
    """A LoggerGroup represents a group of loggers."""

    loggers: list[Logger]
    level: int
    disabled: bool
    processor: Incomplete | None

    def __init__(
        self,
        loggers: list[Logger] | None = None,
        level: int = ...,
        processor: Incomplete | None = None,
    ) -> None: ...
    def add_logger(self, logger: Logger) -> None: ...
    def remove_logger(self, logger: Logger) -> None: ...
    def process_record(self, record: LogRecord) -> None: ...

class Processor:
    """A context manager that processes log records with a given function."""

    def __init__(self, callback: Callable[[LogRecord], None]) -> None: ...
    def __enter__(self) -> Processor: ...
    def __exit__(self, exc_type: object, exc_value: object, tb: object) -> None: ...

class ContextObject:
    """An object that can be bound to a context."""

    stack_manager: Incomplete | None

    def push_context(self) -> None: ...
    def pop_context(self) -> None: ...
    def push_application(self) -> None: ...
    def pop_application(self) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(self, exc_type: object, exc_value: object, tb: object) -> None: ...

class Flags:
    """Allows flags to be pushed on a flag stack."""

    stack_manager: Incomplete

    def __init__(self, **flags: Incomplete) -> None: ...
    @staticmethod
    def get_flag(flag: str, default: Incomplete = ...) -> Incomplete: ...
    def push_application(self) -> None: ...
    def pop_application(self) -> None: ...
    def push_context(self) -> None: ...
    def pop_context(self) -> None: ...
    def __enter__(self) -> Flags: ...
    def __exit__(self, exc_type: object, exc_value: object, tb: object) -> None: ...

__all__ = [
    'CRITICAL',
    'DEBUG',
    'ERROR',
    'INFO',
    'NOTICE',
    'NOTSET',
    'TRACE',
    'WARNING',
    'StringLevel',
    'NumericLevel',
    'LogLevel',
    'LogFilter',
    'LogRecord',
    'Logger',
    'LoggerGroup',
    'Processor',
    'ContextObject',
    'Flags',
]
