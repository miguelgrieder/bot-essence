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


def waha_get(path: str, timeout: Optional[int] = None) -> requests.Response:
    url = f"{settings.waha_url}{path}"
    effective_timeout = timeout if timeout is not None else DEFAULT_WAHA_TIMEOUT
    return requests.get(url=url, headers=_waha_headers(), timeout=effective_timeout)


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


def get_group_info(chat_id: str) -> dict[str, Any]:
    """Fetch group info (name/subject, description, and picture url if available) using WAHA GET /api/{session}/groups/{id}.
    Returns a dict with keys: name, description, picture_url.
    """
    session = "default"
    path = f"/api/{session}/groups/{chat_id}"
    try:
        resp = waha_get(path)
        # Attempt JSON parse safely
        content_type = resp.headers.get("content-type", "")
        data: dict[str, Any] = resp.json()
    except Exception as e:
        log.exception("Failed to get group info for %s: %s", chat_id, e)
        data = {}
    # Normalize typical fields from possible WAHA payloads
    name = data["name"]
    description = data["groupMetadata"]["desc"]
    picture_url = get_group_picture(chat_id)["url"]
    return {"name": name, "description": description, "picture_url": picture_url}


def send_file_by_url(
    chat_id: str, url: str, caption: str | None = None, file_name: str | None = None
) -> requests.Response:
    """Minimal helper to send a file by URL (commonly used for images)."""
    payload: dict[str, Any] = {
        "session": "default",
        "chatId": chat_id,
        "url": url,
    }
    if caption:
        payload["text"] = caption
    if file_name:
        payload["fileName"] = file_name
    return waha_post("/api/sendFile", json=payload)


def get_group_picture(chat_id: str, refresh: bool = False) -> dict[str, Any]:
    """Fetch group picture using WAHA GET /api/{session}/groups/{id}/picture.
    Returns a dict with key: url (string) or empty string on failure.
    """
    session = "default"
    # Query string only when True to avoid potential rate limits
    qs = "?refresh=true" if refresh else ""
    path = f"/api/{session}/groups/{chat_id}/picture{qs}"
    try:
        resp = waha_get(path)
        data = resp.json()
        url = (data or {}).get("url") or ""
    except Exception as e:
        log.exception("Failed to get group picture for %s: %s", chat_id, e)
        url = ""
    return {"url": url}
