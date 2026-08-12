"""
Logbook handler that sends event to Sentry (https://docs.sentry.io/)

.. note::
    This module is only available when the ``sentry`` extra is installed::

        pip install chameleon_log[sentry]

If the ``sentry`` extra is not installed, ``SentryHandler`` will be available
but will be a no-op handler that does nothing.
"""

from __future__ import annotations

import importlib.util
import warnings
from typing import TYPE_CHECKING

from logbook.handlers import Handler


if TYPE_CHECKING:
    from logbook.base import LogRecord


# Check if sentry-sdk is available
_SENTRY_AVAILABLE = importlib.util.find_spec('sentry_sdk') is not None

if not _SENTRY_AVAILABLE:
    warnings.warn(
        'The sentry-sdk package is not installed. '
        'The SentryHandler will not forward logs to Sentry. '
        'To enable Sentry support, install the sentry extra: '
        'pip install chameleon_log[sentry]',
        UserWarning,
        stacklevel=2,
    )

# Map Logbook level numbers (and names) to Sentry event ``level`` values.
# Mirrors ``sentry_sdk.integrations.logging.LOGGING_TO_EVENT_LEVEL``, with
# Logbook's extra levels ``TRACE`` and ``NOTICE`` folded onto the closest match.
_LOGBOOK_LEVEL_TO_EVENT_LEVEL: dict[int | str, str] = {}

# Values accepted by Sentry for the ``level`` event field.
_VALID_EVENT_LEVELS = frozenset(('debug', 'info', 'warning', 'error', 'fatal'))

if _SENTRY_AVAILABLE:
    import sentry_sdk
    from sentry_sdk.utils import capture_internal_exceptions, event_from_exception, to_string

    _LOGBOOK_LEVEL_TO_EVENT_LEVEL.update(
        {
            0: 'notset',
            'NOTSET': 'notset',
            9: 'debug',
            10: 'debug',
            11: 'info',
            12: 'info',
            13: 'warning',
            14: 'error',
            15: 'fatal',
            'TRACE': 'debug',
            'DEBUG': 'debug',
            'INFO': 'info',
            'NOTICE': 'info',
            'WARNING': 'warning',
            'ERROR': 'error',
            'CRITICAL': 'fatal',
        }
    )


class SentryHandler(Handler):
    """
    `Logbook`_ handler that forwards log records to `Sentry`_.

    Use this handler when you want Sentry events to be created directly from
    Logbook records. The ``sentry-sdk`` logging integration hooks into the
    stdlib :mod:`logging` module by monkey-patching
    ``logging.Logger.callHandlers``. Logbook dispatches records through its
    own ``Logger.call_handlers`` chain instead, so the stdlib integration
    will not see records that flow only through Logbook. Push this handler
    onto the stacked handler with ``with handler:`` to forward records to
    Sentry::

        import logbook
        import sentry_sdk
        from chameleon_log.sentry import SentryHandler

        sentry_sdk.init(dsn='...')
        logger = logbook.Logger('myapp')
        handler = SentryHandler(level=logbook.ERROR)

        with handler:
            logger.error('Failed to connect')

    Behavior is modelled after
    ``sentry_sdk.integrations.logging.EventHandler``: records carrying an
    exception are sent as events with a stacktrace, while ordinary records
    become events with the Logbook channel, level, formatted message and any
    ``extra`` fields attached.

    If the ``sentry`` extra is not installed, this handler acts as a no-op
    (does nothing) but remains available to prevent import errors.

    :param level: Log level filter (default: ``NOTSET``)
    :param filter: Optional log filter function (default: ``None``)
    :param bubble: Continue dispatching to subsequent handlers (default: ``False``)

    .. _Logbook: https://logbook.readthedocs.io/
    .. _Sentry: https://docs.sentry.io/
    """

    # Follow sentry_sdk.integrations.logging.EventHandler.
    def emit(self, record: LogRecord) -> None:
        # Skip if sentry-sdk is not available (no-op mode)
        if not _SENTRY_AVAILABLE:
            return

        with capture_internal_exceptions():
            self._emit(record)

    def _emit(self, record: LogRecord) -> None:
        client = sentry_sdk.get_client()
        if not client.is_active():
            return

        # Make sure ``exc_info=True`` has been resolved into a tuple and that
        # ``message``/``time``/``frame`` are populated when ``emit`` is called
        # directly (outside of Logbook's dispatcher, which would normally do
        # this for us).
        if not record.heavy_initialized:
            record.heavy_init()

        client_options = client.options

        exc_info = record.exc_info
        if isinstance(exc_info, tuple) and exc_info[0] is not None:
            event, hint = event_from_exception(
                exc_info,
                client_options=client_options,
                mechanism={'type': 'logging', 'handled': True},
            )
        else:
            event = {}
            hint = {}

        hint['log_record'] = record

        level = _LOGBOOK_LEVEL_TO_EVENT_LEVEL.get(
            record.level, _LOGBOOK_LEVEL_TO_EVENT_LEVEL.get(record.level_name, 'info')
        )
        if level in _VALID_EVENT_LEVELS:
            event['level'] = level  # type: ignore[typeddict-item]
        event['logger'] = record.channel

        event['logentry'] = {
            'message': to_string(record.msg),
            'formatted': record.message,
            'params': record.args,
        }

        extra: dict[str, object] = dict(record.extra) if record.extra else {}
        event['extra'] = extra

        sentry_sdk.capture_event(event, hint=hint)  # type: ignore[arg-type]


__all__ = ('SentryHandler',)
