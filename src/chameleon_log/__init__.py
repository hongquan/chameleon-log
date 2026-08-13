__version__ = '3.0.0'

from .detectors import get_log_handler, is_connected_journald
from .rich import RichHandler


__all__ = ('RichHandler', 'get_log_handler', 'is_connected_journald')
