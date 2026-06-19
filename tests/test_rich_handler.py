from io import StringIO

import logbook
from rich.console import Console

from chameleon_log import RichHandler


class TTYStringIO(StringIO):
    def isatty(self) -> bool:
        return True


def test_rich_handler(logger: logbook.Logger) -> None:
    stream = StringIO()
    console = Console(file=stream, force_terminal=True, color_system='standard', highlight=True)
    handler = RichHandler(console=console)
    with handler:
        logger.error('An error')
        logger.warning('A warning')
        logger.debug('A debug message')
        lines = stream.getvalue().rstrip('\n').splitlines()

    # Rich outputs ANSI escape codes for colors when console is provided
    assert len(lines) == 3
    assert 'An error' in lines[0]
    assert 'A warning' in lines[1]
    assert 'A debug message' in lines[2]
    assert '\x1b[' in lines[0]
    assert '\x1b[' in lines[1]
    assert '\x1b[' in lines[2]


def test_rich_handler_exception(logger: logbook.Logger) -> None:
    """Test that logger.exception captures and formats exceptions in Rich style."""
    stream = StringIO()
    console = Console(file=stream, force_terminal=True, color_system='standard', highlight=True)
    handler = RichHandler(console=console, rich_tracebacks=True)
    with handler:
        try:
            raise ValueError('Test exception message')
        except ValueError:
            logger.exception('An exception occurred')
        output = stream.getvalue()

    assert 'An exception occurred' in output
    assert 'ValueError' in output
    assert '\x1b[' in output


def test_rich_handler_rich_tracebacks_can_be_enabled_in_constructor(logger: logbook.Logger) -> None:
    """Test that rich_tracebacks can be enabled when the handler is created."""
    stream = StringIO()
    console = Console(file=stream, force_terminal=True, color_system='standard', highlight=True)
    handler = RichHandler(console=console, rich_tracebacks=True)

    with handler:
        try:
            raise ValueError('Test exception message')
        except ValueError:
            logger.exception('An exception occurred')

    output = stream.getvalue()

    assert 'An exception occurred' in output
    assert 'ValueError' in output
    assert '\x1b[' in output


def test_rich_handler_exception_without_rich_tracebacks(logger: logbook.Logger) -> None:
    """Test that logger.exception appends tracebacks when Rich tracebacks are disabled."""
    stream = StringIO()
    handler = RichHandler(stream=stream, console=False)
    with handler:
        handler.rich_tracebacks = False
        try:
            raise ValueError('Test exception message')
        except ValueError:
            logger.exception('An exception occurred')
        output = stream.getvalue()

    assert 'An exception occurred' in output
    assert 'Traceback (most recent call last):' in output
    assert 'ValueError: Test exception message' in output
    assert '\x1b[' not in output


def test_rich_handler_dict_highlighting(logger: logbook.Logger) -> None:
    """Test that dictionaries are highlighted by Rich when logged."""
    stream = StringIO()
    console = Console(file=stream, force_terminal=True, color_system='standard', highlight=True)
    handler = RichHandler(console=console)
    with handler:
        logger.info('Dict log: {}', {'a': 1, 'b': 'A string'})
        output = stream.getvalue()

    assert 'Dict log:' in output
    assert "'a'" in output
    assert '1' in output
    assert "'b'" in output
    assert "'A string'" in output
    assert '\x1b[' in output


def test_rich_handler_disables_highlighting_for_non_tty_stream(logger: logbook.Logger) -> None:
    """Test that console=True (auto) disables highlighting for non-TTY streams."""
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
    """Test that console=False disables Rich formatting even for TTY streams."""
    stream = TTYStringIO()
    handler = RichHandler(stream=stream, console=False)

    with handler:
        logger.warning('Plain output: {}', {'a': 1})

    output = stream.getvalue()

    assert 'Plain output:' in output
    assert "'a'" in output
    assert '1' in output
    assert '\x1b[' not in output


def test_rich_handler_on_enables_rich_formatting_for_non_tty(logger: logbook.Logger) -> None:
    """Test that passing a Console enables Rich formatting even for non-TTY streams."""
    stream = StringIO()
    console = Console(file=stream, force_terminal=True, color_system='standard', highlight=True)
    handler = RichHandler(console=console)

    with handler:
        logger.warning('Forced output: {}', {'a': 1})

    output = stream.getvalue()

    assert 'Forced output:' in output
    assert "'a'" in output
    assert '1' in output
    assert '\x1b[' in output


def test_rich_handler_with_shared_console(logger: logbook.Logger) -> None:
    """Test that a shared Console can be passed to RichHandler for use with progress bars."""
    stream = StringIO()
    shared_console = Console(file=stream, force_terminal=True, color_system='standard', highlight=True)
    handler = RichHandler(console=shared_console)

    assert handler.console is shared_console

    with handler:
        logger.info('Log alongside progress')
        output = stream.getvalue()

    assert 'Log alongside progress' in output
    assert '\x1b[' in output


def test_rich_handler_console_true_defaults_to_global_when_terminal_rendering() -> None:
    """Test that when console=True and terminal rendering is active, the global console is used."""
    from rich import get_console

    handler = RichHandler(stream=TTYStringIO(), console=True)
    assert handler.console is get_console()


def test_rich_handler_console_true_non_tty_returns_none() -> None:
    """Test that console=True with non-TTY stream falls back to plain output."""
    handler = RichHandler(stream=StringIO(), console=True)
    assert handler.console is None


def test_rich_handler_console_false_returns_none() -> None:
    """Test that console=False means the console property returns None."""
    handler = RichHandler(console=False)
    assert handler.console is None
