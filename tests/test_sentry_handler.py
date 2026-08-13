from __future__ import annotations

import inspect
from collections.abc import Iterator
from typing import TYPE_CHECKING

import logbook
import pytest
import sentry_sdk
import sentry_sdk.scope as _scope_mod
from logbook.handlers import Handler
from sentry_sdk.envelope import Envelope
from sentry_sdk.transport import Transport

import chameleon_log.sentry as sentry_module


if TYPE_CHECKING:
    from pytest_mock import MockerFixture


class _DropTransport(Transport):
    """A Sentry transport that drops every envelope on the floor."""

    __test__ = False  # tell pytest not to collect this as a test class

    def __init__(self) -> None:
        Transport.__init__(self)

    def capture_envelope(self, envelope: Envelope) -> None:
        """Discard the envelope."""


class _SentryInit:
    """Callable returned by the ``sentry_init`` fixture (mimic upstream's API)."""

    def __call__(self, *args: object, **kwargs: object) -> None:
        kwargs.setdefault('transport', _DropTransport())
        client = sentry_sdk.Client(*args, **kwargs)  # type: ignore[arg-type]
        sentry_sdk.get_global_scope().set_client(client)


@pytest.fixture(autouse=True)
def _clean_scopes() -> None:
    """Reset Sentry scope state between tests so fixtures don't bleed."""
    _scope_mod._global_scope = None
    _scope_mod._isolation_scope.set(None)
    _scope_mod._current_scope.set(None)


@pytest.fixture
def sentry_init() -> Iterator[_SentryInit]:
    """Initialize ``sentry_sdk`` with a no-op transport for the test's duration.

    Provides a callable that accepts the same args/kwargs as
    :class:`sentry_sdk.Client`. Pattern matches the upstream sentry-python
    ``sentry_init`` fixture so this codebase reuses familiar idioms.
    """
    old_client = sentry_sdk.get_global_scope().client
    sentry_sdk.get_current_scope().set_client(None)
    try:
        yield _SentryInit()
    finally:
        sentry_sdk.get_global_scope().set_client(old_client)


@pytest.fixture
def capture_events(sentry_init: _SentryInit, monkeypatch: pytest.MonkeyPatch) -> list[dict]:
    """Return a list of JSON payloads for every captured Sentry event."""
    sentry_init()
    events: list[dict] = []
    client = sentry_sdk.get_client()
    assert client.transport is not None  # noqa: S101  -- _DropTransport is set above.
    original_capture_envelope = client.transport.capture_envelope

    def _capture(envelope: Envelope) -> None:
        for item in envelope:
            headers_type = item.headers.get('type') if item.headers else None
            if headers_type in ('event', 'transaction'):
                payload = item.payload.json
                if payload is not None:
                    events.append(payload)
        original_capture_envelope(envelope)

    monkeypatch.setattr(client.transport, 'capture_envelope', _capture)
    return events


def test_sentry_handler_is_a_logbook_handler() -> None:
    handler = sentry_module.SentryHandler()
    assert isinstance(handler, Handler)


def test_sentry_handler_captures_event(capture_events: list[dict], logger: logbook.Logger) -> None:
    handler = sentry_module.SentryHandler(level=logbook.INFO)

    with handler:
        logger.info('hello world')

    assert len(capture_events) == 1
    event = capture_events[0]
    assert event['logger'] == 'testlogger'
    assert event['level'] == 'info'
    assert event['logentry']['formatted'] == 'hello world'
    assert event['logentry']['message'] == 'hello world'
    assert event['logentry']['params'] == []  # noqa: PLC1802,PLR2004  -- JSON round-tripped from ().


def test_sentry_handler_includes_extra_fields(capture_events: list[dict], logger: logbook.Logger) -> None:
    handler = sentry_module.SentryHandler(level=logbook.INFO)

    with handler:
        logger.info('with extras', extra={'farm': 'tomato'})

    assert len(capture_events) == 1
    event = capture_events[0]
    assert event['extra'].get('farm') == 'tomato'


def test_sentry_handler_sends_exception(capture_events: list[dict], logger: logbook.Logger) -> None:
    handler = sentry_module.SentryHandler(level=logbook.ERROR)

    with handler:
        try:
            raise ValueError('boom')
        except ValueError:
            logger.exception('failed')

    assert len(capture_events) == 1
    event = capture_events[0]
    assert event['exception'] is not None
    mechanism = event.get('exception', {}).get('values', [{}])[0].get('mechanism', {})
    assert mechanism == {'type': 'logbook', 'handled': True}
    assert event['level'] == 'error'
    assert event['logger'] == 'testlogger'
    assert event['logentry']['formatted'] == 'failed'


def test_sentry_handler_respects_level_filter(capture_events: list[dict], logger: logbook.Logger) -> None:
    handler = sentry_module.SentryHandler(level=logbook.ERROR)

    with handler:
        logger.info('filtered out')
        logger.error('captured')

    assert len(capture_events) == 1
    event = capture_events[0]
    assert event['logentry']['formatted'] == 'captured'


def test_sentry_handler_ignores_inactive_client(
    sentry_init: _SentryInit, logger: logbook.Logger, mocker: MockerFixture
) -> None:
    """When the live client reports itself inactive the handler is a no-op."""
    sentry_init()
    mocker.patch.object(sentry_sdk.get_client(), 'is_active', return_value=False)

    handler = sentry_module.SentryHandler(level=logbook.INFO)
    with handler:
        logger.info('ignored')


def _log_helper() -> None:
    logbook.Logger('testlogger').info('captured here')  # noqa: LOG015


def test_sentry_handler_forwards_logbook_source_location(
    capture_events: list[dict],
) -> None:
    handler = sentry_module.SentryHandler(level=logbook.INFO)

    with handler:
        _log_helper()

    assert len(capture_events) == 1
    event = capture_events[0]
    extra = event['extra']
    helper_lines, _ = inspect.getsourcelines(_log_helper)
    log_call_line = next(i for i, line in enumerate(helper_lines, start=1) if 'info(' in line)
    helper_lineno = _log_helper.__code__.co_firstlineno + log_call_line - 1
    assert extra['logbook.func_name'] == '_log_helper'
    assert extra['logbook.module'] == __name__
    assert isinstance(extra['logbook.lineno'], int)
    assert extra['logbook.lineno'] == helper_lineno
    assert extra['logbook.filename'].endswith('test_sentry_handler.py')
    assert extra['logbook.thread'] is not None


def test_sentry_handler_does_not_clobber_caller_extra_keys(capture_events: list[dict], logger: logbook.Logger) -> None:
    handler = sentry_module.SentryHandler(level=logbook.INFO)

    with handler:
        logger.info('caller wins', extra={'logbook.filename': 'user-supplied'})

    assert len(capture_events) == 1
    assert capture_events[0]['extra']['logbook.filename'] == 'user-supplied'


def test_sentry_handler_translates_logbook_levels(capture_events: list[dict], logger: logbook.Logger) -> None:
    handler = sentry_module.SentryHandler(level=logbook.NOTSET)

    with handler:
        logger.debug('debug-msg')
        logger.notice('notice-msg')
        logger.warning('warn-msg')
        logger.critical('crit-msg')

    assert [event['level'] for event in capture_events] == ['debug', 'info', 'warning', 'fatal']
