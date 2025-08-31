from bot_essence.logging.local import configure_logging

from .version import VERSION

configure_logging()


__version__ = VERSION


__all__ = [
    "__version__",
]
