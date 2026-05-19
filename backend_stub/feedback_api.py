from __future__ import annotations

import json
import os
from typing import Any

from aiohttp import web

from backend_stub.telegram_auth import (
    TelegramAuthError,
    build_safe_webapp_user,
    extract_telegram_user_id,
    validate_telegram_init_data,
)
from telegram_bot.services.feedback import (
    compact_feedback_message,
    validate_feedback_category,
    validate_feedback_message,
)
from telegram_bot.storage.feedback_data import create_feedback_ticket, get_user_feedback


INIT_DATA_HEADER = "X-Telegram-Init-Data"


def setup_feedback_routes(app: web.Application) -> None:
    app.router.add_post("/api/feedback", create_feedback)
    app.router.add_get("/api/feedback/my", my_feedback)


async def create_feedback(request: web.Request) -> web.Response:
    session = _feedback_session_from_request(request)
    if isinstance(session, web.Response):
        return session

    body = await _read_json_body(request)
    category = str(body.get("category") or "").strip()
    is_category_valid, _ = validate_feedback_category(category)
    if not is_category_valid:
        return _json_error("invalid_category", status=400)

    message = str(body.get("message") or "").strip()
    is_message_valid, message_error = validate_feedback_message(message)
    if not is_message_valid:
        return _json_error(_feedback_message_error_code(message_error), status=400)

    context = body.get("context")
    safe_context = context if isinstance(context, dict) else {}
    safe_context["session_mode"] = session["mode"]

    ticket = create_feedback_ticket(
        source="mini_app",
        user_id=session["user_id"],
        user_name=session["user_name"],
        category=category,
        message=message,
        context=safe_context,
    )
    return _json_response(
        {
            "status": "ok",
            "mode": session["mode"],
            "ticket": _public_ticket(ticket),
        }
    )


async def my_feedback(request: web.Request) -> web.Response:
    session = _feedback_session_from_request(request, allow_local=True)
    if isinstance(session, web.Response):
        return session

    if session["mode"] == "local" or session["user_id"] is None:
        return _json_response({"status": "ok", "mode": "local", "tickets": []})

    tickets = [_public_ticket(ticket, include_message=True) for ticket in get_user_feedback(session["user_id"], limit=5)]
    return _json_response({"status": "ok", "mode": "telegram", "tickets": tickets})


def _feedback_session_from_request(request: web.Request, allow_local: bool = True) -> dict[str, Any] | web.Response:
    init_data = request.headers.get(INIT_DATA_HEADER, "")
    if not init_data:
        if allow_local:
            return {"mode": "local", "user_id": None, "user_name": None}
        return _json_error("unauthorized", status=401)

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        return _json_error("bot_token_not_configured", status=503)

    try:
        validated = validate_telegram_init_data(init_data, token)
    except TelegramAuthError:
        return _json_error("invalid_init_data", status=401)

    user_id = extract_telegram_user_id(validated)
    if user_id is None:
        return _json_error("invalid_init_data", status=401)

    user = build_safe_webapp_user(validated)
    user_name = " ".join(
        str(user.get(field) or "").strip()
        for field in ("first_name", "last_name")
        if str(user.get(field) or "").strip()
    ).strip()
    if not user_name and user.get("username"):
        user_name = f"@{user['username']}"

    return {"mode": "telegram", "user_id": user_id, "user_name": user_name or None}


async def _read_json_body(request: web.Request) -> dict[str, Any]:
    try:
        body = await request.json()
    except json.JSONDecodeError as error:
        raise web.HTTPBadRequest(
            text=_json_dumps({"status": "error", "error": "invalid_json"}),
            content_type="application/json",
        ) from error
    return body if isinstance(body, dict) else {}


def _public_ticket(ticket: dict[str, Any], include_message: bool = False) -> dict[str, Any]:
    public = {
        "ticket_id": ticket.get("ticket_id"),
        "status": ticket.get("status"),
        "category_label": ticket.get("category_label"),
        "created_at": ticket.get("created_at"),
    }
    if include_message:
        public["message"] = compact_feedback_message(str(ticket.get("message") or ""))
    return public


def _feedback_message_error_code(message_error: str) -> str:
    if "длин" in message_error:
        return "message_too_long"
    if "подробнее" in message_error:
        return "message_too_short"
    return "invalid_message"


def _json_error(message: str, status: int) -> web.Response:
    return _json_response({"status": "error", "error": message}, status=status)


def _json_response(data: dict[str, Any], status: int = 200) -> web.Response:
    return web.json_response(data, status=status, dumps=_json_dumps)


def _json_dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False)
