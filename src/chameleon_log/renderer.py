from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Callable

from rich._log_render import LogRender as _LogRender
from rich.console import Console, ConsoleRenderable, Group
from rich.containers import Renderables
from rich.table import Table
from rich.text import Text


class LogRender(_LogRender):
    """Custom log renderer that optimizes layout for multi-line content.

    Differences from the original `rich._log_render.LogRender`:

    - Displays the file path on the same row as the first renderable (typically
      the log message), avoiding wasted right space for continued lines.
    - Subsequent renderables (e.g., tracebacks) are rendered full-width without
      a file path column, allowing them to use the entire available width.
    """

    def __call__(  # type: ignore[override]
        self,
        console: Console,
        renderables: Iterable[ConsoleRenderable],
        log_time: datetime | None = None,
        time_format: str | Callable[[datetime], Text] | None = None,
        level: str | Text = '',
        path: str | None = None,
        line_no: int | None = None,
        link_path: str | None = None,
    ) -> ConsoleRenderable:
        renderable_list = tuple(renderables) or (Text(''),)

        first_row = self.render_row(
            console=console,
            renderable=renderable_list[0],
            log_time=log_time,
            time_format=time_format,
            level=level,
            path=path,
            line_no=line_no,
            link_path=link_path,
        )
        if len(renderable_list) == 1:
            return first_row
        return Group(
            first_row,
            self.render_row(
                console=console,
                renderable=Renderables(renderable_list[1:]),
                log_time=log_time,
                time_format=time_format,
                level='',
            ),
        )

    def render_row(
        self,
        *,
        console: Console,
        renderable: ConsoleRenderable,
        log_time: datetime | None,
        time_format: str | Callable[[datetime], Text] | None,
        level: str | Text,
        path: str | None = None,
        line_no: int | None = None,
        link_path: str | None = None,
    ) -> Table:
        output = Table.grid(padding=(0, 1))
        output.expand = True
        if self.show_time:
            output.add_column(style='log.time')
        if self.show_level:
            output.add_column(style='log.level', width=self.level_width)
        output.add_column(ratio=1, style='log.message', overflow='fold')
        if self.show_path and path:
            output.add_column(style='log.path')

        row: list[ConsoleRenderable] = []
        if self.show_time:
            current_time = log_time or console.get_datetime()
            current_time_format = time_format or self.time_format
            if callable(current_time_format):
                log_time_display = current_time_format(current_time)
            else:
                log_time_display = Text(current_time.strftime(current_time_format))
            if log_time_display == self._last_time and self.omit_repeated_times:
                row.append(Text(' ' * len(log_time_display)))
            else:
                row.append(log_time_display)
                self._last_time = log_time_display
        if self.show_level:
            row.append(level if isinstance(level, Text) else Text(level))

        row.append(renderable)
        if self.show_path and path:
            path_text = Text()
            path_text.append(path, style=f'link file://{link_path}' if link_path else '')
            if line_no:
                path_text.append(':')
                path_text.append(
                    f'{line_no}',
                    style=f'link file://{link_path}#{line_no}' if link_path else '',
                )
            row.append(path_text)

        output.add_row(*row)
        return output
