#!/usr/bin/env python3
"""Combined example using JournaldHandler and SentryHandler together.

In production a service typically wants to:

* Persist structured logs locally through systemd journal (``journalctl``
  lets operators query the latest state of the service, attach extra
  fields, and follow logs in real time).
* Forward errors to Sentry so the team gets alerted and gets full
  context (stacktraces, extra fields, release tags, etc.).

Both handlers can be stacked with Logbook's ``with`` block so a single
``logger.error(...)`` call ends up in both places without any extra
plumbing. During development a ``RichHandler`` is usually enough.

The example prints each captured Sentry event to stdout when ``SENTRY_DSN``
is unset, so it is runnable without a Sentry account. Journald still
requires Linux + systemd + the ``journald-send`` package. ``sudo`` is
optional — either run as ``root`` to write to the system journal, or run
as a user unit (``systemctl --user``) to write to the user journal.
"""

from __future__ import annotations

import json
import os

import logbook
import sentry_sdk

from chameleon_log.journald import JournaldHandler
from chameleon_log.sentry import SentryHandler


def main() -> None:
    """Demo running JournaldHandler and SentryHandler side by side."""

    # Sentry setup ------------------------------------------------------------
    # If SENTRY_DSN is set, events are forwarded to your Sentry project.
    # Otherwise a placeholder DSN is used so events still flow through the
    # pipeline; ``before_send`` then prints each event to stdout instead of
    # sending it. This keeps the example runnable without a Sentry account.
    dsn = os.getenv('SENTRY_DSN') or 'https://public@example.com/1'
    sending = 'SENTRY_DSN' in os.environ

    def before_send(event, _hint):  # noqa: ANN001,ANN202  -- accept arbitrary event payloads.
        """Print each captured event to stdout when not sending to Sentry."""
        print('--- Sentry event ---')
        print(json.dumps(event, indent=2, default=str, sort_keys=True))
        return event if sending else None

    sentry_sdk.init(dsn=dsn, before_send=before_send)

    # Handler setup -----------------------------------------------------------
    # ``JournaldHandler`` keeps the local, structured trail of every record.
    # ``SentryHandler`` is filtered to WARNING and above so noisy ``INFO``
    # messages do not flood Sentry. Extras carried on the record flow through
    # to both destinations: journald stores them as F_* fields and Sentry
    # attaches them under ``event.extra``.
    journald_handler = JournaldHandler(syslog_identifier='chameleon-log-combined')
    sentry_handler = SentryHandler(level=logbook.WARNING)

    with journald_handler, sentry_handler:
        logger = logbook.Logger('com.example.combined')

        # Plain log call: ends up in journald only (below Sentry threshold).
        logger.info('Application started successfully')

        # ``extra`` is forwarded to both handlers: journald sees F_USER_ID /
        # F_PLAN fields, Sentry sees them as ``event.extra``.
        logger.warning(
            'User signed in: {}',
            'alice',
            extra={'user_id': 42, 'plan': 'free'},
        )

        # Exception: Sentry receives a full event with stacktrace; journald
        # stores the formatted message and the traceback text.
        try:
            int('abc')
        except ValueError:
            logger.exception('Failed to convert string to integer')

        # A Processor injects the same context into a batch of records without
        # repeating the ``extra=`` argument. Useful for request-scoped data
        # such as ``request_id`` that should land in both destinations.
        def inject_request_context(record: logbook.LogRecord) -> None:
            """Simulate per-request metadata being attached to every record."""
            record.extra['request_id'] = 'req-7f3c'
            record.extra['route'] = '/api/v1/orders'

        with logbook.Processor(inject_request_context):
            logger.info('Order created')
            logger.error('Order validation failed')


if __name__ == '__main__':
    main()
