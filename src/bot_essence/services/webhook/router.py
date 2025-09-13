import logging
from typing import Any

from fastapi import APIRouter

from bot_essence.services.webhook.controller import handle_message

log = logging.getLogger(__name__)

router = APIRouter()


@router.post("/")
def waha_webhook_router(body: dict[str, Any]) -> dict[str, Any]:
    payload = body.get("payload") or {}
    event_type = payload.get("status") or payload.get("event") or body.get("event")
    log.info(f"Received webhook {event_type}: {body}")

    event_to_function = {
        "message": handle_message,
    }
    if event_to_function.get(event_type):
        return event_to_function[event_type](body)
    else:
        return {"status": "success", "processed": True}
