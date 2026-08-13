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

import logbook
from logbook.base import lookup_level as lookup_logbook_level
from logbook.handlers import Handler


if TYPE_CHECKING:
    from logbook.base import LogFilter, LogLevel, LogRecord, NumericLevel
    from sentry_sdk._types import LogLevelStr


# Check if sentry-sdk is available
_SENTRY_AVAILABLE = importlib.util.find_spec('sentry_sdk') is not None

# Defer the missing-sentry-sdk warning until a handler is actually instantiated so
# importing :mod:`chameleon_log` does not emit warnings for callers that never use
# Sentry. ``warnings.warn`` deduplicates identical messages at the same source
# location under the default filter, so multiple instantiations still warn once.


# Map Logbook level numbers to Sentry event ``level`` values.
# Mirrors ``sentry_sdk.integrations.logging.LOGGING_TO_EVENT_LEVEL``, with
# Logbook's extra levels ``TRACE`` and ``NOTICE`` folded onto the closest match.
# Records at levels outside this mapping (e.g. ``NOTSET`` or user-defined
# levels) are dropped by :class:`SentryHandler`.
LOGBOOK_LEVEL_TO_EVENT_LEVEL: dict[NumericLevel, LogLevelStr] = {
    logbook.TRACE: 'debug',
    logbook.DEBUG: 'debug',
    logbook.INFO: 'info',
    logbook.NOTICE: 'info',
    logbook.WARNING: 'warning',
    logbook.ERROR: 'error',
    logbook.CRITICAL: 'fatal',
}


if _SENTRY_AVAILABLE:
    import sentry_sdk
    from sentry_sdk.utils import capture_internal_exceptions, event_from_exception, to_string


class SentryHandler(Handler):
    """
    `Logbook`_ handler that forwards log records to `Sentry`_.

    Use this handler when you want Sentry events to be created directly from
    Logbook records. The ``sentry-sdk`` logging integration only hooks into
    the stdlib :mod:`logging` module by monkey-patching
    ``logging.Logger.callHandlers``. Logbook dispatches records through its
    own ``Logger.call_handlers`` chain instead, so the stdlib integration
    does not see records that flow only through Logbook. Bind the handler to
    Logbook's application stack with a ``with`` block to forward records to
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
    become events tagged with the Logbook channel, level, formatted message
    and any ``extra`` fields.

    The handler only emits events when the Sentry client is configured and
    active; emits from an unconfigured client are silently dropped.

    If the ``sentry`` extra is not installed, this handler remains importable
    and silently no-ops instead of raising.

    :param level: Minimum Logbook level for records to forward. Defaults to
        ``WARNING`` so that routine operational noise is filtered out and
        only noteworthy events reach Sentry.
    :param filter: Optional :class:`logbook.base.LogFilter` used to further
        restrict which records are forwarded.
    :param bubble: Continue dispatching to subsequent handlers (default: ``False``)

    .. _Logbook: https://logbook.readthedocs.io/
    .. _Sentry: https://docs.sentry.io/
    """

    def __init__(
        self, level: LogLevel = logbook.WARNING, filter: LogFilter | None = None, bubble: bool = False
    ) -> None:
        # Default level is WARNING because we often interested in errors when using Sentry.
        super().__init__(level, filter, bubble)

        if not _SENTRY_AVAILABLE:
            warnings.warn(
                'The sentry-sdk package is not installed. '
                'SentryHandler will not forward logs to Sentry. '
                'To enable Sentry support, install the sentry extra: '
                'pip install chameleon_log[sentry]',
                UserWarning,
                stacklevel=2,
            )

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

        client_options = client.options

        exc_info = record.exc_info
        if isinstance(exc_info, tuple) and exc_info[0] is not None:
            event, hint = event_from_exception(
                exc_info,
                client_options=client_options,
                mechanism={'type': 'logbook', 'handled': True},
            )
        # Records without an exception (exc_info is None or not a tuple) intentionally
        # omit a current-thread stacktrace: Logbook records already carry their own
        # source-location data and attaching the caller's stacktrace produces noisier,
        # redundant events in Sentry.
        else:
            event = {}
            hint = {}

        hint['log_record'] = record
        int_level = lookup_logbook_level(record.level)

        try:
            level = LOGBOOK_LEVEL_TO_EVENT_LEVEL[int_level]
        except KeyError:
            # Skip posting event of unknown level.
            return
        event['level'] = level
        event['logger'] = record.channel

        event['logentry'] = {
            'message': to_string(record.msg),
            'formatted': record.message,
            'params': record.args,
        }

        extra: dict[str, object] = dict(record.extra) if record.extra is not None else {}
        event['extra'] = extra

        sentry_sdk.capture_event(event, hint=hint)


__all__ = ('SentryHandler',)
