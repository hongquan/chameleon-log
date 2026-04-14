"""
Journald handler for Logbook.

This module provides a handler that sends Logbook log records to the systemd
`journald`_ with rich metadata and structured data support.

.. note::
    This module is only available when the ``journald`` extra is installed::

        pip install chameleon_log[journald]

If the ``journald`` extra is not installed, the ``JournaldHandler`` will be available
but will be a no-op handler that does nothing.

.. _journald: https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html
"""

from __future__ import annotations

import importlib.util
from typing import TYPE_CHECKING

from logbook.handlers import Handler


if TYPE_CHECKING:
    from logbook.base import LogRecord
    from logbook.handlers import LogFilter


# Check if journald-send is available
_JOURNALD_AVAILABLE = importlib.util.find_spec('journald_send') is not None

LEVEL_TO_PRIORITY: dict[str, int] = {}

if _JOURNALD_AVAILABLE:
    import journald_send
    from journald_send import Priority

    LEVEL_TO_PRIORITY = {
        'DEBUG': Priority.DEBUG,
        'INFO': Priority.INFO,
        'WARNING': Priority.WARNING,
        'ERROR': Priority.ERROR,
        'EXCEPTION': Priority.ERROR,
        'CRITICAL': Priority.CRITICAL,
        'NOTICE': Priority.NOTICE,
        'TRACE': Priority.DEBUG,
        'NOTSET': Priority.INFO,
    }

    DEFAULT_PRIORITY = Priority.INFO

    def send_to_standard_journal(
        message: str,
        priority: Priority | None = None,
        code_file: str | None = None,
        code_line: int | None = None,
        code_func: str | None = None,
        **kwargs: object,
    ) -> None:
        """Send a message to journald using journald_send.send."""
        journald_send.send(
            message, priority=priority, code_file=code_file, code_line=code_line, code_func=code_func, **kwargs
        )

else:
    # No-op functions when journald-send is not available
    def send_to_standard_journal(
        message: str,
        priority: int | None = None,
        code_file: str | None = None,
        code_line: int | None = None,
        code_func: str | None = None,
    ) -> None:  # type: ignore[misc]
        """No-op function when journald_send is not available."""
        pass


class JournaldHandler(Handler):
    """
    `Logbook`_ handler to write log to `journald`_.

    This handler sends log records to the systemd journal (`journald`_) with rich
    metadata. It includes standard fields like ``CODE_FILE``, ``CODE_LINE``, etc., as
    well as any extra fields from the log record.

    Extra field names are automatically uppercased by the handler. For example,
    if you add extra data with key ``farm``, it will be stored as ``F_FARM`` in
    `journald`_ (assuming the default prefix ``f_``). You can then filter logs
    using ``journalctl`` with the uppercase field name.

    If the ``journald`` extra is not installed, this handler acts as a no-op
    (does nothing) but remains available to prevent import errors.

    :param level: Log level filter (default: 0)
    :type level: ``int`` | ``str``
    :param filter: Optional log filter function (default: ``None``)
    :type filter: LogFilter | ``None``
    :param bubble: Whether to bubble logs to parent handlers (default: ``False``)
    :type bubble: ``bool``
    :param syslog_identifier: Optional syslog identifier for the logs (default: ``None``)
    :type syslog_identifier: ``str`` | ``None``
    :param extra_field_prefix: Prefix for extra fields (default: ``f_``). Will be automatically uppercased.
    :type extra_field_prefix: ``str``

    .. _Logbook: https://logbook.readthedocs.io/
    .. _journald: https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html
    """

    def __init__(
        self,
        level: int | str = 0,
        filter: LogFilter | None = None,
        bubble: bool = False,
        syslog_identifier: str | None = None,
        extra_field_prefix: str = 'f_',
    ) -> None:
        # Call parent init to properly initialize the handler
        super().__init__(level=level, filter=filter, bubble=bubble)
        self.syslog_identifier = syslog_identifier
        self.extra_field_prefix = extra_field_prefix

    def emit(self, record: LogRecord) -> None:
        # Skip if journald is not available (no-op mode)
        if not _JOURNALD_AVAILABLE:
            return

        # Get the message
        message = record.message

        # Append exception to message if present
        if record.exc_info:
            if formatted_exception := record.formatted_exception:
                message = f'{message}\n{formatted_exception}'

        # Convert level name to journald priority
        try:
            priority = Priority(LEVEL_TO_PRIORITY[record.level_name])
        except (KeyError, ValueError):
            priority = DEFAULT_PRIORITY

        # Send to journald
        kwargs: dict[str, object] = {
            'LOGGER': record.channel.rsplit('.', 1)[-1] if record.channel else '',
            'THREAD_NAME': record.thread_name or 'main',
            'PROCESS_NAME': record.process_name or 'python',
            'MODULE': record.module or '__main__',
            'LEVEL': record.level_name,
            # Do not send `TIMESTAMP` because journald tracks the time itself.
        }
        if self.syslog_identifier:
            kwargs['SYSLOG_IDENTIFIER'] = self.syslog_identifier
        if record.exc_info:
            if formatted_exception := record.formatted_exception:
                kwargs['EXCEPTION_TEXT'] = formatted_exception
        # Add extra fields from log record
        if record.extra:
            for key, value in record.extra.items():
                kwargs[f'{self.extra_field_prefix}{key}'.upper()] = value
        send_to_standard_journal(
            message,
            priority,
            code_file=record.filename or 'example.py',
            code_line=record.lineno or 0,
            code_func=record.func_name or 'main',
            **kwargs,
        )


__all__ = ('JournaldHandler',)
