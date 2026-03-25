from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import logbook
from logbook import LogRecord
from logbook.compat import LoggingHandler as _LoggingHandler


if TYPE_CHECKING:
    from logbook.handlers import LogFilter


class StdLoggingHandler(_LoggingHandler):
    """
    Handler for logbook which redirect messages to standard logging module.
    This is to fix the original logbook's LoggingHandler, which tranfers
    all message to the root logger, instead of equivalent channels.
    """

    def __init__(
        self,
        logger: logging.Logger | None = None,
        level: int = logbook.NOTSET,
        filter: LogFilter | None = None,
        bubble: bool = False,
    ) -> None:
        super().__init__(logger, level, filter, bubble)
        self.sublogs: dict[str, logging.Logger] = {}

    def get_logger(self, record: LogRecord) -> logging.Logger:
        name = record.channel
        if not name:
            return self.logger
        logger = self.sublogs.get(name)
        if not logger:
            logger = logging.getLogger(name)
            self.sublogs[name] = logger
        return logger
