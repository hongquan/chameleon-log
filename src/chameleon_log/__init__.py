__version__ = '1.1.3'

from .detectors import is_connected_journald
from .rich import RichHandler


__all__ = ('RichHandler', 'is_connected_journald')
