from io import StringIO

from rich.console import Console
from rich.text import Text

from chameleon_log.renderer import LogRender


def test_log_render_keeps_path_on_first_row_and_blanks_continuation_level() -> None:
    stream = StringIO()
    console = Console(file=stream, force_terminal=True, width=80, color_system='standard')
    render = LogRender(show_time=False, show_level=True, show_path=True)

    result = render(
        console,
        [Text('hello'), Text('world'), Text('boom')],
        level=Text('INFO'),
        path='example.py',
        line_no=12,
    )

    console.print(result)
    output = stream.getvalue()

    assert output.count('INFO') == 1
    assert output.count('example.py') == 1
    assert 'hello' in output
    assert 'world' in output
    assert 'boom' in output
