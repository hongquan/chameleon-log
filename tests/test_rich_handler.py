from io import StringIO

import logbook

from chameleon_log import RichHandler, RichRendering


class TTYStringIO(StringIO):
    def isatty(self) -> bool:
        return True


def test_rich_handler(logger: logbook.Logger) -> None:
    stream = StringIO()
    handler = RichHandler(stream=stream, rich_rendering=RichRendering.ON)
    with handler:
        logger.error('An error')
        logger.warning('A warning')
        logger.debug('A debug message')
        lines = stream.getvalue().rstrip('\n').splitlines()

    # Rich outputs ANSI escape codes for colors when rich_rendering='on'
    # Check that output contains the messages and ANSI codes
    assert len(lines) == 3
    assert 'An error' in lines[0]
    assert 'A warning' in lines[1]
    assert 'A debug message' in lines[2]
    # Verify ANSI codes are present (Rich colors)
    assert '\x1b[' in lines[0]
    assert '\x1b[' in lines[1]
    assert '\x1b[' in lines[2]


def test_rich_handler_exception(logger: logbook.Logger) -> None:
    """Test that logger.exception captures and formats exceptions in Rich style."""
    stream = StringIO()
    handler = RichHandler(stream=stream, rich_rendering=RichRendering.ON)
    with handler:
        handler.rich_tracebacks = True
        try:
            raise ValueError('Test exception message')
        except ValueError:
            logger.exception('An exception occurred')
        output = stream.getvalue()

    # Verify the log message is present
    assert 'An exception occurred' in output
    # Verify exception info is present (Rich formats traceback with styled output)
    assert 'ValueError' in output
    # Verify ANSI codes are present (Rich formatting)
    assert '\x1b[' in output


def test_rich_handler_dict_highlighting(logger: logbook.Logger) -> None:
    """Test that dictionaries are highlighted by Rich when logged."""
    stream = StringIO()
    handler = RichHandler(stream=stream, rich_rendering=RichRendering.ON)
    with handler:
        logger.info('Dict log: {}', {'a': 1, 'b': 'A string'})
        output = stream.getvalue()

    # Verify the log message is present
    assert 'Dict log:' in output
    # Verify dict values are present and highlighted
    assert "'a'" in output
    assert '1' in output
    assert "'b'" in output
    assert "'A string'" in output
    # Verify ANSI codes are present (Rich highlighting)
    assert '\x1b[' in output


def test_rich_handler_disables_highlighting_for_non_tty_stream(logger: logbook.Logger) -> None:
    """Test that rich_rendering=None (auto) disables highlighting for non-TTY streams."""
    stream = StringIO()
    handler = RichHandler(stream=stream)

    with handler:
        logger.warning('Redirected output: {}', {'a': 1})

    output = stream.getvalue()

    assert 'Redirected' in output
    assert 'output:' in output
    assert "'a'" in output
    assert '1' in output
    assert '\x1b[' not in output


def test_rich_handler_off_disables_rich_formatting(logger: logbook.Logger) -> None:
    """Test that rich_rendering='off' disables Rich formatting even for TTY streams."""
    stream = TTYStringIO()
    handler = RichHandler(stream=stream, rich_rendering=RichRendering.OFF)

    with handler:
        logger.warning('Plain output: {}', {'a': 1})

    output = stream.getvalue()

    assert 'Plain output:' in output
    assert "'a'" in output
    assert '1' in output
    assert '\x1b[' not in output


def test_rich_handler_on_enables_rich_formatting_for_non_tty(logger: logbook.Logger) -> None:
    """Test that rich_rendering='on' enables Rich formatting even for non-TTY streams."""
    stream = StringIO()
    handler = RichHandler(stream=stream, rich_rendering=RichRendering.ON)

    with handler:
        logger.warning('Forced output: {}', {'a': 1})

    output = stream.getvalue()

    assert 'Forced output:' in output
    assert "'a'" in output
    assert '1' in output
    assert '\x1b[' in output
