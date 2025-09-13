import logging
from typing import Any, Optional

import requests

from bot_essence import config

settings = config.get_settings()
log = logging.getLogger(__name__)


# Unified WAHA request caller to manage auth headers and timeout
DEFAULT_WAHA_TIMEOUT = 30


def _waha_headers(extra: Optional[dict[str, str]] = None) -> dict[str, str]:
    headers: dict[str, str] = {
        "X-Api-Key": settings.waha_token,
        "Content-Type": "application/json",
    }
    if extra:
        headers.update(extra)
    return headers


def waha_post(path: str, json: dict[str, Any], timeout: Optional[int] = None) -> requests.Response:
    url = f"{settings.waha_url}{path}"
    effective_timeout = timeout if timeout is not None else DEFAULT_WAHA_TIMEOUT
    return requests.post(url=url, json=json, headers=_waha_headers(), timeout=effective_timeout)


def send_message(chat_id: str, message: str) -> requests.Response:
    payload = {
        "session": "default",
        "chatId": chat_id,
        "text": message,
    }
    return waha_post("/api/sendText", json=payload)


def start_typing(chat_id: str) -> requests.Response:
    payload = {
        "session": "default",
        "chatId": chat_id,
    }
    return waha_post("/api/startTyping", json=payload)


def stop_typing(chat_id: str) -> requests.Response:
    payload = {
        "session": "default",
        "chatId": chat_id,
    }
    return waha_post("/api/stopTyping", json=payload)
