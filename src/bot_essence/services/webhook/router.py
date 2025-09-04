import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter

from bot_essence import config
from bot_essence.services.webhook.controller import send_message, start_typing, stop_typing

log = logging.getLogger(__name__)

router = APIRouter()


def is_group_chat(chat_id: str) -> bool:
    # WhatsApp convention: groups end with "@g.us", privates end with "@c.us"
    return chat_id.endswith("@g.us")


def get_self_jid(body: dict[str, Any]) -> Optional[str]:
    # Prefer configured self id, fallback to any info possibly present in webhook body
    settings = config.get_settings()
    if settings.waha_self_id:
        return settings.waha_self_id

    # Try common locations where WAHA might include instance/bot id
    # Keep it robust and optional – return None if not found
    instance = body.get("instance") or {}
    me = instance.get("me") or {}
    me_id = me.get("id") or me.get("jid") or me.get("user")
    if isinstance(me_id, str) and me_id:
        return me_id

    # Some payloads might carry self id under payload["sender"]/"owner"
    payload = body.get("payload") or {}
    for key in ("owner", "sender", "fromMeJid", "botJid"):
        val = payload.get(key)
        if isinstance(val, str) and val:
            return val

    return None


def extract_text(payload: Dict[str, Any]) -> str:
    # Simple text extraction with safe defaults
    text = payload.get("body")
    if isinstance(text, str):
        return text
    # Try alternative fields if present
    return str(text) if text is not None else ""


def group_message_targets_me(payload: Dict[str, Any], self_jid: Optional[str]) -> bool:
    # If we don't know self_jid, try best-effort via context flags
    context = payload.get("context") or payload.get("contextInfo") or {}

    # 1) Check explicit mentions list
    mentions = (
        payload.get("mentionedJidList")
        or payload.get("mentions")
        or context.get("mentionedJidList")
        or []
    )
    if (
        self_jid
        and isinstance(mentions, list)
        and any(m == self_jid for m in mentions if isinstance(m, str))
    ):
        return True

    # 2) Check if it's a reply to our message
    # Many WA libs include flags like fromMe, quotedFromMe or contextInfo.fromMe for replied message
    quoted_from_me = (
        payload.get("quotedFromMe") or context.get("quotedFromMe") or context.get("fromMe")
    )
    if isinstance(quoted_from_me, bool) and quoted_from_me:
        return True

    # Some payloads carry participant info for quoted messages
    quoted_participant = (
        context.get("quotedParticipant")
        or context.get("participant")
        or payload.get("quotedParticipant")
    )
    if self_jid and isinstance(quoted_participant, str) and quoted_participant == self_jid:
        return True

    # 3) Heuristic: if text starts with an @mention of our number (when self_jid like 123@c.us)
    text = extract_text(payload)
    if self_jid and text:
        possible_num = self_jid.split("@")[0]
        if possible_num and (f"@{possible_num}" in text.replace(" ", "")):
            return True

    return False


def handle_private_message(body: dict[str, Any]) -> dict[str, Any]:
    payload = body.get("payload") or {}
    chat_id = payload.get("from") or payload.get("chatId") or ""
    text = extract_text(payload)

    # Simulate typing and reply
    if isinstance(chat_id, str) and chat_id:
        start_typing(chat_id=chat_id)
        response = f"Resposta Automática :) - {text}"
        send_message(chat_id=chat_id, message=response)
        stop_typing(chat_id=chat_id)

    return {
        "status": "success",
        "processed": True,
        "chat_type": "private",
        "chat_id": chat_id,
        "received_text": text,
    }


def handle_group_message(body: dict[str, Any]) -> dict[str, Any]:
    payload = body.get("payload") or {}
    chat_id = payload.get("from") or payload.get("chatId") or ""
    text = extract_text(payload)
    self_jid = get_self_jid(body)

    directed = group_message_targets_me(payload, self_jid)

    if directed and isinstance(chat_id, str) and chat_id:
        start_typing(chat_id=chat_id)
        response = f"(grupo) Resposta Automática :) - {text}"
        send_message(chat_id=chat_id, message=response)
        stop_typing(chat_id=chat_id)

    return {
        "status": "success",
        "processed": bool(directed),
        "reason": None if directed else "ignored: not mentioning nor replying to the bot",
        "chat_type": "group",
        "chat_id": chat_id,
        "received_text": text,
        "self_jid": self_jid,
    }


def handle_message(body: dict[str, Any]) -> dict[str, Any]:
    if is_group_chat(body.get("chatId") or ""):
        return handle_group_message(body)
    else:
        return handle_private_message(body)


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
