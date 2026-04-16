__version__ = '1.7.1'

from .detectors import is_connected_journald
from .rich import RichHandler


__all__ = ('RichHandler', 'is_connected_journald')
