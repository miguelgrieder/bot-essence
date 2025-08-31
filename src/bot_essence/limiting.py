from functools import lru_cache
from typing import Any

from slowapi import Limiter

from bot_essence import config

settings = config.get_settings()


def limiting_key_function(*args: Any, **kwargs: Any) -> str:
    return "*"


@lru_cache(1)
def get_limiter() -> Limiter:
    return Limiter(
        key_func=limiting_key_function,
        enabled=settings.rate_limiter_enabled,
    )
