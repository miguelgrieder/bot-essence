import logging
from typing import Any

from fastapi import APIRouter

from bot_essence.services.activities.controller import send_message, start_typing, stop_typing

log = logging.getLogger(__name__)

router = APIRouter()


@router.post("/")
def waha_webhook_router(body: dict[str, Any]) -> dict[str, str]:

    chat_id = body["payload"]["from"]
    received_message = body["payload"]["body"]

    start_typing(chat_id=chat_id)

    response = f"Resposta Automática :) - {received_message}"
    send_message(
        chat_id=chat_id,
        message=response,
    )
    stop_typing(chat_id=chat_id)

    return {"status": "success"}
