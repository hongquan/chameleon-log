from __future__ import annotations

from typing import cast

import logbook
import pytest
import pytest_mock

import chameleon_log.journald as journald_module


@pytest.mark.skipif(not journald_module._JOURNALD_AVAILABLE, reason='systemd-python not installed')
def test_journald_handler_appends_exception_to_message(
    logger: logbook.Logger,
    mocker: pytest_mock.MockerFixture,
) -> None:
    sent_calls: list[tuple[str, int, dict[str, object]]] = []

    def capture_journal_send(message: str, priority: int, **extra_fields: object) -> None:
        sent_calls.append((message, priority, extra_fields))

    handler = journald_module.JournaldHandler(syslog_identifier='test-service')

    # Patch the function directly
    mocker.patch.object(journald_module, 'send_to_standard_journal', side_effect=capture_journal_send)

    with handler:
        try:
            raise ValueError('Test exception message')
        except ValueError:
            logger.exception('An exception occurred')

    assert len(sent_calls) == 1

    message, _, extra_fields = sent_calls[0]

    assert 'An exception occurred' in message
    assert '\n' in message
    assert 'ValueError: Test exception message' in message
    assert 'EXCEPTION_INFO' not in extra_fields
    # EXCEPTION_TEXT is added to extra_fields for structured logging
    assert 'EXCEPTION_TEXT' in extra_fields
    exception_text = cast(str, extra_fields['EXCEPTION_TEXT'])
    assert 'Traceback' in exception_text
    assert 'ValueError: Test exception message' in exception_text


@pytest.mark.skipif(not journald_module._JOURNALD_AVAILABLE, reason='systemd-python not installed')
def test_journald_handler_preserves_message_without_exception(
    logger: logbook.Logger,
    mocker: pytest_mock.MockerFixture,
) -> None:
    sent_calls: list[tuple[str, int, dict[str, object]]] = []

    def capture_journal_send(message: str, priority: int, **extra_fields: object) -> None:
        sent_calls.append((message, priority, extra_fields))

    handler = journald_module.JournaldHandler(syslog_identifier='test-service')

    # Patch the function directly
    mocker.patch.object(journald_module, 'send_to_standard_journal', side_effect=capture_journal_send)

    with handler:
        logger.info('Plain message')

    assert len(sent_calls) == 1

    message, _, extra_fields = sent_calls[0]

    assert message == 'Plain message'
    assert 'EXCEPTION_INFO' not in extra_fields
    assert 'EXCEPTION_TEXT' not in extra_fields
