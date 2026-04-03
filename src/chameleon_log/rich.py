from __future__ import annotations

import sys
from http import HTTPMethod
from pathlib import Path
from typing import IO, TYPE_CHECKING

from logbook.base import (
    NOTSET,
    LogRecord,
)
from logbook.handlers import StreamHandler
from rich._log_render import LogRender
from rich.console import Console, ConsoleRenderable
from rich.highlighter import ReprHighlighter
from rich.text import Text
from rich.traceback import Traceback


if TYPE_CHECKING:
    # Import type definitions from stubs for type checking only
    from logbook.base import LogLevel
    from logbook.handlers import LogFilter


class RichHandler(StreamHandler):
    """
    A Logbook handler that renders colored, formatted log output using `Rich`_.

    This handler extends Logbook's StreamHandler to provide rich terminal output
    with features like:

    - Colored log levels with 8-character width (via ``ljust(8)``)
    - Syntax highlighting for log messages
    - Clickable file paths with line numbers
    - Optional tracebacks with rich formatting
    - HTTP method keyword highlighting

    The handler automatically detects if it's outputting to a terminal and
    disables colors/formatting when redirecting to files or non-TTY streams.

    :param level: Log level filter (default: ``NOTSET``)
    :type level: LogLevel
    :param filter: Optional log filter function (default: ``None``)
    :type filter: LogFilter | None
    :param bubble: Whether to bubble logs to parent handlers (default: ``False``)
    :type bubble: bool
    :param stream: Output stream (default: ``sys.stderr``)
    :type stream: IO[str] | None
    :param enable_link_path: Enable clickable file paths in terminal (default: ``True``)
    :type enable_link_path: bool
    :param rich_rendering: Control Rich rendering mode (default: ``None``)
        - ``True``: Always use Rich colorful rendering
        - ``False``: Disable Rich formatting, render plain output
        - ``None``: Auto-detect based on ``isatty()``
    :type rich_rendering: bool | None

    Example usage::

        import logbook
        from chameleon_log import RichHandler

        logger = logbook.Logger('MyApp')
        handler = RichHandler()

        with handler:
            logger.info('Application started')
            logger.warning('Low disk space')
            logger.error('Connection failed')

    .. _Rich: https://github.com/Textualize/rich
    """

    def __init__(
        self,
        level: LogLevel = NOTSET,
        filter: LogFilter | None = None,
        bubble: bool = False,
        *,
        stream: IO[str] | None = None,
        enable_link_path: bool = True,
        rich_rendering: bool | None = None,
    ) -> None:
        super().__init__(
            stream=stream if stream is not None else sys.stderr,
            level=level,
            filter=filter,
            bubble=bubble,
        )
        self.rich_rendering: bool | None = rich_rendering
        self._console: Console | None = None
        self.highlighter = ReprHighlighter()
        self.log_render = LogRender(
            show_time=True,
            # For development, it is not practical to show date part.
            time_format='[%X]',
            show_level=True,
            show_path=True,
            omit_repeated_times=True,
            # level_width controlled by get_level_text() via ljust(8)
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
        self.keywords = tuple(HTTPMethod)

    def use_terminal_rendering(self) -> bool:
        if self.rich_rendering is True:
            return True

        if self.rich_rendering is False:
            return False

        isatty = getattr(self.stream, 'isatty', None)
        if not callable(isatty):
            return False
        result = isatty()
        return bool(result)

    def format(self, record: LogRecord) -> str:
        channel_name = record.channel.rsplit('.', 1)[-1] if record.channel else ''
        return f'{channel_name}: {record.message}'

    @property
    def console(self) -> Console | None:
        if self._console is None and self.use_terminal_rendering():
            self._console = Console(
                file=self.stream,
                force_terminal=self.rich_rendering is True,
                color_system='standard',
                highlight=True,
            )
        return self._console

    def emit(self, record: LogRecord) -> None:
        message = self.format(record)
        if not self.console:
            self.write_plain(message)
            return
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
        message_renderable = self.render_message(record, message)
        log_renderable = self.render(
            record=record, console=self.console, traceback=traceback, message_renderable=message_renderable
        )
        self.lock.acquire()
        try:
            self.ensure_stream_is_open()
            self.console.print(log_renderable)
            if self.should_flush():
                self.flush()
        finally:
            self.lock.release()

    def write_plain(self, message: str) -> None:
        """
        Write plain message (no color)
        """
        self.lock.acquire()
        try:
            self.ensure_stream_is_open()
            self.stream.write(message)
            self.stream.write('\n')
            if self.should_flush():
                self.flush()
        finally:
            self.lock.release()

    # Ported from rich.logging
    def render_message(self, record: LogRecord, message: str) -> ConsoleRenderable:
        """Render message text in to ``Text``.

        :param record: logbook ``Record``.
        :type record: LogRecord
        :param message: String containing log message.
        :type message: str
        :return: Renderable to display log message.
        """
        use_markup = getattr(record, 'markup', self.use_markup)
        message_text = Text.from_markup(message) if use_markup else Text(message)

        highlighter = getattr(record, 'highlighter', self.highlighter)
        if highlighter:
            message_text = highlighter(message_text)

        if self.keywords:
            message_text.highlight_words(self.keywords, 'logging.keyword')

        return message_text

    # Ported from rich.logging
    def render(
        self,
        *,
        record: LogRecord,
        console: Console,
        traceback: Traceback | None,
        message_renderable: ConsoleRenderable,
    ) -> ConsoleRenderable:
        """Render log for display.

        :param record: logbook ``Record``.
        :type record: LogRecord
        :param traceback: ``Traceback`` instance or ``None`` for no Traceback.
        :type traceback: Traceback | None
        :param message_renderable: Renderable (typically ``Text``) containing log message contents.
        :type message_renderable: ConsoleRenderable
        :return: Renderable to display log.
        """
        path = Path(record.filename or '/opt').name
        level_text = self.get_level_text(record)

        log_renderable = self.log_render(
            console,
            [message_renderable] if not traceback else [message_renderable, traceback],
            log_time=record.time,
            level=level_text,
            path=path,
            line_no=record.lineno,
            link_path=record.filename if self.enable_link_path else None,
        )
        return log_renderable

    def get_level_text(self, record: LogRecord) -> Text:
        """Get the level name from the record as a styled ``Text`` object.

        :param record: logbook ``Record``.
        :type record: LogRecord
        :return: A ``Text`` instance containing the level name with appropriate styling.
        """
        level_name = record.level_name
        level_text = Text.styled(level_name.ljust(8), f'logging.level.{level_name.lower()}')
        return level_text
