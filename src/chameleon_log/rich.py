from __future__ import annotations

import sys
from http import HTTPMethod
from pathlib import Path
from typing import IO, Callable, Literal

from logbook.base import NOTSET, LogRecord
from logbook.handlers import Handler, StreamHandler
from rich._log_render import LogRender
from rich.console import Console, ConsoleRenderable
from rich.highlighter import ReprHighlighter
from rich.text import Text
from rich.traceback import Traceback


type StringLevel = Literal['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTICE', 'TRACE', 'NOTSET']
type NumericLevel = Literal[15, 14, 13, 12, 11, 10, 9, 0]
type LogLevel = StringLevel | NumericLevel


type LogFilter = Callable[[LogRecord, Handler], bool]

# Similar to original logbook DEFAULT_FORMAT_STRING, but without the `{record.time}`,
# and `{record.level_name}` because they will be rendered at side, by rich's `LogRender`. 
DEFAULT_FORMAT_STRING = (
    "{record.channel}: {record.message}"
)

class RichHandler(StreamHandler):
    def __init__(
        self,
        level: LogLevel = NOTSET,
        filter: LogFilter | None = None,
        bubble: bool = False,
        *,
        stream: IO[str] | None = None,
        enable_link_path: bool = True,
        force_terminal: bool = False,
    ) -> None:
        super().__init__(
            stream=stream if stream is not None else sys.stderr,
            level=level,
            format_string=DEFAULT_FORMAT_STRING,
            filter=filter,
            bubble=bubble,
        )
        # Only allow to set `force_terminal` once.
        self._force_terminal = force_terminal
        self._console: Console | None = None
        self.highlighter = ReprHighlighter()
        self._log_render = LogRender(
            show_time=True,
            show_level=True,
            show_path=True,
            omit_repeated_times=True,
            level_width=None,
        )
        self.enable_link_path = enable_link_path
        # These attributes are for Rich. We don't let configurable yet.
        self.use_markup = False
        self.rich_tracebacks = False
        self.tracebacks_width = None
        self.tracebacks_extra_lines = 3
        self.tracebacks_theme = None
        self.tracebacks_word_wrap = True
        self.tracebacks_show_locals = False
        self.tracebacks_suppress = ()
        self.tracebacks_max_frames = 100
        self.tracebacks_code_width = 88
        self.locals_max_length = 10
        self.locals_max_string = 80
        self.keywords = None

    def use_terminal_rendering(self) -> bool:
        if self._force_terminal:
            return True

        isatty = getattr(self.stream, 'isatty', None)
        return callable(isatty) and isatty()

    @property
    def console(self) -> Console:
        if self._console is None:
            use_terminal_rendering = self.use_terminal_rendering()
            self._console = Console(
                file=self.stream,
                force_terminal=self._force_terminal,
                color_system='standard' if use_terminal_rendering else None,
                highlight=use_terminal_rendering,
            )
        return self._console

    def emit(self, record: LogRecord) -> None:
        message = self.format(record)
        traceback: Traceback | None = None
        if (
            self.rich_tracebacks
            and record.exc_info
            and record.exc_info != (None, None, None)
            and record.exc_info is not True
        ):
            exc_type, exc_value, exc_traceback = record.exc_info
            assert exc_type is not None
            assert exc_value is not None
            traceback = Traceback.from_exception(
                exc_type,
                exc_value,
                exc_traceback,
                width=self.tracebacks_width,
                code_width=self.tracebacks_code_width,
                extra_lines=self.tracebacks_extra_lines,
                theme=self.tracebacks_theme,
                word_wrap=self.tracebacks_word_wrap,
                show_locals=self.tracebacks_show_locals,
                locals_max_length=self.locals_max_length,
                locals_max_string=self.locals_max_string,
                suppress=self.tracebacks_suppress,
                max_frames=self.tracebacks_max_frames,
            )
            message = record.message
        message_renderable = self.render_message(record, message)
        log_renderable = self.render(
            record=record, traceback=traceback, message_renderable=message_renderable
        )
        self.lock.acquire()
        try:
            self.ensure_stream_is_open()
            self.console.print(log_renderable)
            if self.should_flush():
                self.flush()
        finally:
            self.lock.release()

    # Ported from rich.logging
    def render_message(self, record: LogRecord, message: str) -> ConsoleRenderable:
        """Render message text in to Text.

        Args:
            record (LogRecord): logbook Record.
            message (str): String containing log message.

        Returns:
            ConsoleRenderable: Renderable to display log message.
        """
        use_markup = getattr(record, 'markup', self.use_markup)
        message_text = Text.from_markup(message) if use_markup else Text(message)

        highlighter = getattr(record, 'highlighter', self.highlighter)
        if highlighter:
            message_text = highlighter(message_text)

        if self.keywords is None:
            self.keywords = tuple(HTTPMethod)

        if self.keywords:
            message_text.highlight_words(self.keywords, 'logging.keyword')

        return message_text

    # Ported from rich.logging
    def render(
        self,
        *,
        record: LogRecord,
        traceback: Traceback | None,
        message_renderable: ConsoleRenderable,
    ) -> ConsoleRenderable:
        """Render log for display.

        Args:
            record (LogRecord): logbook Record.
            traceback (Optional[Traceback]): Traceback instance or None for no Traceback.
            message_renderable (ConsoleRenderable): Renderable (typically Text) containing log message contents.

        Returns:
            ConsoleRenderable: Renderable to display log.
        """
        path = Path(record.filename or '/opt').name
        level = record.level_name

        log_renderable = self._log_render(
            self.console,
            [message_renderable] if not traceback else [message_renderable, traceback],
            log_time=record.time,
            level=level,
            path=path,
            line_no=record.lineno,
            link_path=record.filename if self.enable_link_path else None,
        )
        return log_renderable
