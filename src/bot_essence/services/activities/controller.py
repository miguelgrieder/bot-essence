import logging
from typing import Any

import requests
from pymongo import MongoClient
from pymongo.collection import Collection

from bot_essence import config

settings = config.get_settings()
log = logging.getLogger(__name__)

# Setup MongoDB connection
client: MongoClient[Any] = MongoClient(
    f"mongodb://{settings.mongo_variables_username}:"
    f"{settings.mongo_variables_password}@"
    f"{settings.mongo_variables_host}:"
    f"{settings.mongo_variables_port}/"
)
db = client["bot-essence"]
activity_collection: Collection[dict[str, Any]] = db["data"]


def send_message(chat_id: str, message: str) -> requests.Response:
    url = f"{settings.waha_url}/api/sendText"
    headers = {
        "X-Api-Key": settings.waha_token,
        "Content-Type": "application/json",
    }
    payload = {
        "session": "default",
        "chatId": chat_id,
        "text": message,
    }
    req = requests.post(
        url=url,
        json=payload,
        headers=headers,
        timeout=30,
    )
    return req


def start_typing(chat_id: str) -> requests.Response:
    url = f"{settings.waha_url}/api/startTyping"
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": settings.waha_token,
    }
    payload = {
        "session": "default",
        "chatId": chat_id,
    }
    req = requests.post(
        url=url,
        json=payload,
        headers=headers,
        timeout=30,
    )
    return req


def stop_typing(chat_id: str) -> requests.Response:
    url = f"{settings.waha_url}/api/stopTyping"
    headers = {
        "X-Api-Key": settings.waha_token,
        "Content-Type": "application/json",
    }
    payload = {
        "session": "default",
        "chatId": chat_id,
    }
    req = requests.post(
        url=url,
        json=payload,
        headers=headers,
        timeout=30,
    )
    return req
