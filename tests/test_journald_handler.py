from __future__ import annotations

import json
import subprocess
import time

import logbook
import pytest

import chameleon_log.journald as journald_module


def query_journal(identifier: str, since: float, code_func: str | None = None) -> list[dict[str, str]]:
    result = subprocess.run(
        [
            'journalctl',
            '--user',
            '-t',
            identifier,
            '--since=@' + str(int(since)),
            '-p',
            'debug',
            '--no-pager',
            '-o',
            'json',
        ],
        capture_output=True,
    )
    entries = [json.loads(ln) for ln in result.stdout.decode().splitlines() if ln.strip()]
    if code_func:
        entries = [e for e in entries if e.get('CODE_FUNC') == code_func]
    return entries


@pytest.mark.skipif(not journald_module._JOURNALD_AVAILABLE, reason='journald-send not installed')
def test_journald_handler_appends_exception_to_message(logger: logbook.Logger) -> None:
    since = time.time()
    handler = journald_module.JournaldHandler(syslog_identifier='chameleon-test')

    with handler:
        try:
            raise ValueError('Test exception message')
        except ValueError:
            logger.exception('An exception occurred')

    entries = query_journal('chameleon-test', since, 'test_journald_handler_appends_exception_to_message')
    assert len(entries) == 1

    msg = entries[0]['MESSAGE']
    assert 'An exception occurred' in msg
    assert '\n' in msg
    assert 'ValueError: Test exception message' in msg

    exc_text = entries[0].get('EXCEPTION_TEXT', '')
    assert 'Traceback' in exc_text
    assert 'ValueError: Test exception message' in exc_text


@pytest.mark.skipif(not journald_module._JOURNALD_AVAILABLE, reason='journald-send not installed')
def test_journald_handler_preserves_message_without_exception(logger: logbook.Logger) -> None:
    since = time.time()
    handler = journald_module.JournaldHandler(syslog_identifier='chameleon-test')

    with handler:
        logger.info('Plain message')

    entries = query_journal('chameleon-test', since, 'test_journald_handler_preserves_message_without_exception')
    assert len(entries) == 1
    assert entries[0]['MESSAGE'] == 'Plain message'
    assert 'EXCEPTION_TEXT' not in entries[0]


@pytest.mark.skipif(not journald_module._JOURNALD_AVAILABLE, reason='journald-send not installed')
def test_journald_handler_includes_metadata(logger: logbook.Logger) -> None:
    since = time.time()
    handler = journald_module.JournaldHandler(syslog_identifier='chameleon-test')

    with handler:
        logger.info('Message with metadata')

    entries = query_journal('chameleon-test', since, 'test_journald_handler_includes_metadata')
    assert len(entries) == 1

    assert 'LOGGER' in entries[0]
    assert entries[0]['LOGGER'] == 'testlogger'
    assert 'THREAD_NAME' in entries[0]
    assert 'PROCESS_NAME' in entries[0]
    assert 'MODULE' in entries[0]
    assert entries[0]['LEVEL'] == 'INFO'
    assert 'SYSLOG_IDENTIFIER' in entries[0]
    assert entries[0]['SYSLOG_IDENTIFIER'] == 'chameleon-test'


@pytest.mark.skipif(not journald_module._JOURNALD_AVAILABLE, reason='journald-send not installed')
def test_journald_handler_sends_extra_fields(logger: logbook.Logger) -> None:
    since = time.time()
    handler = journald_module.JournaldHandler(syslog_identifier='chameleon-test', extra_field_prefix='F_')

    with handler:
        logger.info('Message with extra fields', extra={'farm': 'tomato', 'crop': 'vegetable'})

    entries = query_journal('chameleon-test', since, 'test_journald_handler_sends_extra_fields')
    assert len(entries) == 1

    assert 'F_FARM' in entries[0]
    assert entries[0]['F_FARM'] == 'tomato'
    assert 'F_CROP' in entries[0]
    assert entries[0]['F_CROP'] == 'vegetable'
