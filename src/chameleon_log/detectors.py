from __future__ import annotations

import os
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from logbook import LogLevel

    from .journald import JournaldHandler
    from .rich import RichHandler


def is_connected_journald() -> bool:
    """
    Detect if the current process is connected to systemd journal.

    This function helps developers automatically select the appropriate log handler
    based on the runtime environment. The typical use case is:

    - **Development/Terminal**: Logs should appear in console with pretty formatting
    - **Production/Service**: Logs should go to systemd journal for structured logging

    Detection is based on environment variables: returns ``True`` only when
    ``JOURNAL_STREAM`` is set (indicating journald is available) AND ``TERM``
    is NOT set (indicating we're not in an interactive terminal).

    This enables you to write code that works seamlessly in both environments::

        from chameleon_log import is_connected_journald, RichHandler
        from chameleon_log.journald import JournaldHandler

        # Auto-select handler based on environment
        if is_connected_journald():
            # Production: structured logs in journald
            handler = JournaldHandler(syslog_identifier='my-service')
        else:
            # Development: pretty console output
            handler = RichHandler()

        with handler:
            log.info('Application starting')
            # ... your application code ...

    :return: ``True`` if connected to journald (running as a service), ``False`` otherwise
    """
    # Check if journaled environment variables indicate we're running as a service
    journal_stream = os.getenv('JOURNAL_STREAM')
    if not journal_stream:
        return False
    return not os.getenv('TERM')


def get_log_handler(level: LogLevel = 0, syslog_identifier: str | None = None) -> JournaldHandler | RichHandler:
    """
    Get the appropriate log handler based on the runtime environment.

    Automatically selects between JournaldHandler (for systemd journal) and
    RichHandler (for terminal output) based on whether the process is connected
    to journald.

    :param level: Log level filter (default: 0)
    :type level: LogLevel
    :param syslog_identifier: Optional syslog identifier for journald (default: None)
    :type syslog_identifier: str | None
    :return: JournaldHandler if connected to journald, otherwise RichHandler
    :rtype: JournaldHandler | RichHandler
    """
    if is_connected_journald():
        from .journald import JournaldHandler

        return JournaldHandler(level=level, syslog_identifier=syslog_identifier)

    # If PYTEST_CURRENT_TEST is set, disable Rich's rendering to avoid issues
    # with pytest's output capturing.
    # Otherwise, let RichHandler automatically decide.
    from .rich import RichHandler

    rich_rendering = False if 'PYTEST_CURRENT_TEST' in os.environ else None
    return RichHandler(level=level, rich_rendering=rich_rendering)
