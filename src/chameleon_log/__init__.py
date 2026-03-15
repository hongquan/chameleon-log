__version__ = '1.0.0'

from .rich import RichHandler
from .detectors import is_connected_journald


__all__ = ('RichHandler', 'is_connected_journald')
