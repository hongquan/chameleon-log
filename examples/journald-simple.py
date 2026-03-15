#!/usr/bin/env python3
"""Simple example of using JournaldHandler with Logbook."""

import getpass
import platform

import logbook
from logbook import Logger, Processor

from chameleon_log.journald import JournaldHandler


def do_some_failed_action() -> None:
    """Simulate an action that fails."""
    msg = 'Something went wrong!'
    raise ValueError(msg)


def main() -> None:
    """Main function demonstrating JournaldHandler usage."""
    # Create a JournaldHandler
    handler = JournaldHandler(syslog_identifier='chameleon-log-example')

    with handler:
        # Get a logger
        logger = logbook.Logger('MyApp')

        # Log messages at different levels
        logger.debug('This is a debug message')
        logger.info('Application started successfully')
        logger.notice('This is a notice message')
        logger.warning('This is a warning message')
        logger.error('An error occurred')

        # Example 1: Pass extra fields directly using extra= parameter
        user = getpass.getuser()
        logger.info(
            'Current Linux user: {}',
            user,
            extra={
                'linux': platform.freedesktop_os_release(),
                'platform': platform.platform()
            }
        )

        # Example 2: Use a Processor to inject context into multiple log calls
        def inject_error_context(record: logbook.LogRecord) -> None:
            """Inject error context into log records."""
            record.extra['error_type'] = 'conversion'

        # Log an exception with extra fields using a Processor
        try:
            do_some_failed_action()
        except ValueError:
            with Processor(inject_error_context):
                logger.exception('An error occurred during processing')


if __name__ == '__main__':
    main()
