'''
Journald handler for Logbook.

This module provides a handler that sends Logbook log records to the systemd
journal (journald) with rich metadata and structured data support.

Note: This module is only available when the "journald" extra is installed:
    pip install chameleon_log[journald]

If the journald extra is not installed, the JournaldHandler will be available
but will be a no-op handler that does nothing.
'''

from __future__ import annotations

import datetime
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


    class JournaldHandler(Handler):
        '''
        Logbook handler to write log to journald.
        
        This handler sends log records to the systemd journal (journald) with rich
        metadata. It includes standard fields like CODE_FILE, CODE_LINE, etc., as
        well as any extra fields from the log record.
        
        Extra field names are automatically uppercased by the handler. For example,
        if you add extra data with key ``farm``, it will be stored as ``F_FARM`` in
        journald (assuming the default prefix ``F_``). You can then filter logs
        using journalctl with the uppercase field name.
        
        Parameters:
            level: Log level filter (default: 0)
            filter: Optional log filter function (default: None)
            bubble: Whether to bubble logs to parent handlers (default: False)
            syslog_identifier: Optional syslog identifier for the logs (default: None)
            extra_field_prefix: Prefix for extra fields (default: ``F_``). Must be uppercase.
        '''
        
        def __init__(
            self,
            level: int | str = 0,
            filter: LogFilter | None = None,
            bubble: bool = False,
            syslog_identifier: str | None = None,
            extra_field_prefix: str = 'F_',
        ) -> None:
            # Initialize Handler base attributes directly since base Handler.__init__ doesn't accept these params
            self.level = level
            self.filter = filter
            self.bubble = bubble
            self.syslog_identifier = syslog_identifier
            self.extra_field_prefix = extra_field_prefix

        def emit(self, record: LogRecord) -> None:
            # Get the message
            message = record.message
            
            # Convert level name to journald priority
            priority = LEVEL_TO_PRIORITY.get(record.level_name, journal.LOG_INFO)
            
            # Prepare extra fields for journald
            extra_fields = {
                'LOGGER': record.channel,
                'CODE_FILE': record.filename or 'unknown',
                'CODE_LINE': record.lineno or 0,
                'CODE_FUNC': record.func_name or 'unknown',
                'THREAD_NAME': record.thread_name or 'unknown',
                'PROCESS_NAME': record.process_name or 'unknown',
                'MODULE': record.module or 'unknown',
                'LEVEL': record.level_name,
                'TIMESTAMP': record.time.replace(tzinfo=datetime.timezone.utc) if record.time else datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc),
            }
            
            # Add exception information if present
            if record.exc_info:
                extra_fields['EXCEPTION_TEXT'] = record.formatted_exception or 'Unknown exception'
                extra_fields['EXCEPTION_NAME'] = record.exception_name or 'unknown'
                extra_fields['EXCEPTION_MESSAGE'] = record.exception_message or 'unknown'
            
            # Add extra fields from log record if any
            # record.extra is a defaultdict, so we need to check if it has actual values
            if record.extra and len(record.extra) > 0:
                for key, value in record.extra.items():
                    # Prefix extra fields to avoid conflicts with standard fields
                    extra_fields[f'{self.extra_field_prefix}{key.upper()}'] = value
            
            # Add syslog identifier if provided
            if self.syslog_identifier:
                extra_fields['SYSLOG_IDENTIFIER'] = self.syslog_identifier
            
            # Send to journald
            send_to_standard_journal(message, priority, **extra_fields)

else:
    # No-op handler when systemd-python is not available
    class JournaldHandler(Handler):
        '''
        No-op JournaldHandler when systemd-python is not installed.
        
        This handler is available but does nothing when the "journald" extra is not installed.
        This allows code to use JournaldHandler without crashing if the dependency is missing.
        
        To enable journald logging, install the extra:
            pip install chameleon_log[journald]
        '''
        
        def __init__(
            self,
            level: int | str = 0,
            filter: LogFilter | None = None,
            bubble: bool = False,
            syslog_identifier: str | None = None,
            extra_field_prefix: str = 'F_',
        ) -> None:
            # Initialize attributes but don't use them
            self.level = level
            self.filter = filter
            self.bubble = bubble
            self.syslog_identifier = syslog_identifier
            self.extra_field_prefix = extra_field_prefix
        
        def emit(self, record: LogRecord) -> None:
            # No-op: do nothing when systemd-python is not available
            pass


__all__ = ('JournaldHandler',)
