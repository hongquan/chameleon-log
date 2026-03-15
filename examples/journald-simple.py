#!/usr/bin/env python3
"""Simple example of using JournaldHandler with Logbook."""

import getpass
import platform

import logbook
from logbook import Processor

from chameleon_log.journald import JournaldHandler


def main() -> None:
    """Main function demonstrating JournaldHandler usage."""
    # Create a JournaldHandler
    handler = JournaldHandler(syslog_identifier='example-simple')

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
            extra={'linux': platform.freedesktop_os_release(), 'platform': platform.platform()},
        )

        # Example 2: Cause an error by calling int('abc') and log the exception
        try:
            # This will raise a ValueError
            int('abc')
        except ValueError:
            logger.exception('Failed to convert string to integer')

        # Example 3: Use a Processor to inject context into multiple log calls
        def inject_error_context(record: logbook.LogRecord) -> None:
            """Inject error context into log records."""
            record.extra['error_type'] = 'conversion'

        def get_optional_message() -> None:
            """Return no message to demonstrate a None-related failure."""
            return None

        # Log an exception with extra fields using a Processor
        try:
            # Another error example
            get_optional_message().strip()  # type: ignore
        except AttributeError:
            with Processor(inject_error_context):
                logger.exception('An error occurred during processing')


if __name__ == '__main__':
    main()
