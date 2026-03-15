
import logging
from typing import Callable, Dict, Optional

import logbook
from logbook import LogRecord
from logbook.compat import LoggingHandler as _LoggingHandler
from logbook.handlers import Handler


type LogFilter = Callable[[LogRecord, Handler], bool]


class StdLoggingHandler(_LoggingHandler):
    '''
    Handler for logbook which redirect messages to standard logging module.
    This is to fix the original logbook's LoggingHandler, which tranfers
    all message to the root logger, instead of equivalent channels.
    '''
    def __init__(
        self, 
        logger: Optional[logging.Logger] = None, 
        level: int = logbook.NOTSET, 
        filter: Optional[LogFilter] = None,
        bubble: bool = False
    ) -> None:
        super().__init__(logger, level, filter, bubble)
        self.sublogs: Dict[str, logging.Handler] = {}

    def get_logger(self, record: LogRecord) -> logging.Handler:
        name = record.channel
        if not name:
            return self.logger
        logger = self.sublogs.get(name)
        if not logger:
            logger = logging.getLogger(name)
            self.sublogs[name] = logger
        return logger
