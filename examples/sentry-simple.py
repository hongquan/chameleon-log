#!/usr/bin/env python3
"""Simple example of using SentryHandler with Logbook."""

from __future__ import annotations

import json
import os

import logbook
import sentry_sdk

from chameleon_log.sentry import SentryHandler


def main() -> None:
    """Main function demonstrating SentryHandler usage."""
    # If SENTRY_DSN is set, events are forwarded to your Sentry project.
    # Otherwise a placeholder DSN is used so that events still flow through
    # the pipeline; ``before_send`` then prints each event to stdout instead
    # of sending it. This keeps the example runnable without a Sentry account.
    dsn = os.getenv('SENTRY_DSN') or 'https://public@example.com/1'
    sending = 'SENTRY_DSN' in os.environ

    def before_send(event, _hint):  # noqa: ANN001,ANN202  -- accept arbitrary event payloads.
        """Print each captured event to stdout when not sending to Sentry."""
        print('--- Sentry event ---')
        print(json.dumps(event, indent=2, default=str, sort_keys=True))
        return event if sending else None

    sentry_sdk.init(dsn=dsn, before_send=before_send)

    handler = SentryHandler(level=logbook.DEBUG)

    with handler:
        logger = logbook.Logger(__name__)

        # Log messages at different levels. Notice folds onto ``info`` and
        # trace folds onto ``debug`` because Sentry has no notion of those
        # Logbook levels.
        logger.debug('This is a debug message')
        logger.info('Application started successfully')
        logger.notice('This is a notice message')
        logger.warning('A non-fatal warning')
        logger.error('Something went wrong')

        # Pass extra fields directly using the extra= parameter. They become
        # entry-level ``extra`` keys on the captured Sentry event.
        logger.info(
            'User signed in: {}',
            'alice',
            extra={'user_id': 42, 'plan': 'free'},
        )

        # Example: Cause an error by calling int('abc') and log the exception.
        # The handler forwards the record to Sentry as an event with a
        # stacktrace and a ``mechanism`` describing it as a handled exception.
        try:
            int('abc')
        except ValueError:
            logger.exception('Failed to convert string to integer')

        # Example: Use a Processor to inject context into multiple log calls
        # without repeating the same extra= argument on each one.
        def inject_error_context(record: logbook.LogRecord) -> None:
            """Inject error context into log records."""
            record.extra['error_type'] = 'conversion'

        def get_optional_message() -> None:
            """Return None to demonstrate a None-related failure."""
            return None

        try:
            get_optional_message().strip()  # type: ignore
        except AttributeError:
            with logbook.Processor(inject_error_context):
                logger.exception('An error occurred during processing')


if __name__ == '__main__':
    main()
