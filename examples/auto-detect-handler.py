#!/usr/bin/env python3
"""
Example demonstrating automatic handler selection based on environment.

This example shows how to use is_connected_journald() to automatically choose
the appropriate handler for different environments:
- Development: RichHandler for pretty console output
- Production (systemd service): JournaldHandler for structured logging
"""

import logbook
from logbook import Logger

from chameleon_log import is_connected_journald, RichHandler
from chameleon_log.journald import JournaldHandler


def main() -> None:
    """
    Automatically select the appropriate handler based on environment.
    
    This pattern allows the same code to work in both development and production.
    """
    # Detect if we're running in a systemd service or terminal
    if is_connected_journald():
        # Production environment: running as systemd service
        print('Detected systemd service environment, using JournaldHandler')
        handler = JournaldHandler(
            syslog_identifier='auto-detect-example',
            extra_field_prefix='F_'
        )
    else:
        # Development environment: running in terminal
        print('Detected terminal environment, using RichHandler')
        handler = RichHandler()

    with handler:
        logger = Logger('MyApp')
        
        logger.info('Application starting...')
        logger.info(f'Handler selected: {handler.__class__.__name__}')
        logger.info('Logs will appear in the appropriate output for the environment')
        
        # Simulate application work with different log levels
        logger.debug('Debug information for troubleshooting')
        logger.notice('Notice: Application is running')
        logger.warning('This is a warning message')
        
        # Log an error with traceback
        try:
            # Simulate an error
            1 / 0
        except ZeroDivisionError:
            logger.exception('An error occurred during execution')
        
        logger.info('Application shutting down')


if __name__ == '__main__':
    main()
