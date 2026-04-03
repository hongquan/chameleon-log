"""
Journald handler for Logbook.

This module provides a handler that sends Logbook log records to the systemd
`journal`_ with rich metadata and structured data support.

.. note::
    This module is only available when the ``journald`` extra is installed::

        pip install chameleon_log[journald]

If the ``journald`` extra is not installed, the ``JournaldHandler`` will be available
but will be a no-op handler that does nothing.

.. _journal: https://www.freedesktop.org/software/systemd/man/systemd-journald.service.html
"""

from __future__ import annotations

import importlib.util
from typing import TYPE_CHECKING

from logbook.handlers import Handler


if TYPE_CHECKING:
    from logbook.base import LogRecord
    from logbook.handlers import LogFilter


# Check if systemd-python is available
_JOURNALD_AVAILABLE = importlib.util.find_spec('systemd') is not None

if _JOURNALD_AVAILABLE:
    from systemd import journal

    LEVEL_TO_PRIORITY = {
        'DEBUG': journal.LOG_DEBUG,
        'INFO': journal.LOG_INFO,
        'WARNING': journal.LOG_WARNING,
        'ERROR': journal.LOG_ERR,
        'EXCEPTION': journal.LOG_ERR,
        'CRITICAL': journal.LOG_CRIT,
        'NOTICE': journal.LOG_NOTICE,
        'TRACE': journal.LOG_DEBUG,
        'NOTSET': journal.LOG_INFO,
        # Other method names will be mapped to 'info' level.
    }

    def send_to_standard_journal(message: str, priority: int, **extra_fields: object) -> None:
        journal.send(message, PRIORITY=priority, **extra_fields)

else:
    # No-op functions when systemd-python is not available
    LEVEL_TO_PRIORITY: dict[str, int] = {}

    def send_to_standard_journal(message: str, priority: int, **extra_fields: object) -> None:  # type: ignore[unused-arg]
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

        # Convert level name to journald priority
        priority = LEVEL_TO_PRIORITY.get(record.level_name, journal.LOG_INFO)

        # Prepare extra fields for journald
        extra_fields = {
            'LOGGER': record.channel.rsplit('.', 1)[-1] if record.channel else '',
            'CODE_FILE': record.filename or 'example.py',
            'CODE_LINE': record.lineno or 0,
            'CODE_FUNC': record.func_name or 'main',
            'THREAD_NAME': record.thread_name or 'main',
            'PROCESS_NAME': record.process_name or 'python',
            'MODULE': record.module or '__main__',
            'LEVEL': record.level_name,
            # Do not send `TIMESTAMP` because journald tracks the time itself.
        }
        # Add syslog identifier if provided
        if self.syslog_identifier:
            extra_fields['SYSLOG_IDENTIFIER'] = self.syslog_identifier

        if record.exc_info:
            # Though we send to `EXCEPTION_TEXT` field, it does not show up in normal view,
            # so we append to message as well.
            if formatted_exception := record.formatted_exception:
                message = f'{message}\n{formatted_exception}'
                extra_fields['EXCEPTION_TEXT'] = formatted_exception

        # Add extra fields from log record if any
        # record.extra is a defaultdict, so we need to check if it has actual values
        if record.extra and len(record.extra) > 0:
            for key, value in record.extra.items():
                # Prefix extra fields to avoid conflicts with standard fields
                # The whole field name will be uppercased to match `journald` requirement.
                extra_fields[f'{self.extra_field_prefix}{key}'.upper()] = value

        # Send to journald
        send_to_standard_journal(message, priority, **extra_fields)


__all__ = ('JournaldHandler',)
