"""Example: RichHandler with a Rich Progress bar.

Demonstrates how to pass a shared ``rich.Console`` to ``RichHandler`` so that
log lines are printed inside a ``rich.progress.Progress`` live display without
breaking the progress bar.
"""

import time

import logbook
from rich.console import Console
from rich.progress import Progress

from chameleon_log import RichHandler


def main() -> None:
    console = Console()
    handler = RichHandler(console=console, rich_tracebacks=True)

    with handler:
        logger = logbook.Logger('download')

        with Progress(console=console) as progress:
            task = progress.add_task('Downloading...', total=100)

            for i in range(1, 11):
                progress.update(task, advance=10)
                if i == 3:
                    logger.info('Checkpoint reached at {}%', i * 10)
                elif i == 7:
                    logger.warning('Slow network detected at {}%', i * 10)
                time.sleep(0.3)

            logger.info('Download complete')


if __name__ == '__main__':
    main()
