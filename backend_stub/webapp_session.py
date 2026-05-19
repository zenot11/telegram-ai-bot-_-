import json
import os
from typing import Any

from aiohttp import web

from backend_stub.telegram_auth import (
    TelegramAuthError,
    build_safe_webapp_user,
    validate_telegram_init_data,
)


INIT_DATA_HEADER = "X-Telegram-Init-Data"


def setup_webapp_session_routes(app: web.Application) -> None:
    app.router.add_get("/api/webapp/session", webapp_session)


async def webapp_session(request: web.Request) -> web.Response:
    init_data = request.headers.get(INIT_DATA_HEADER, "")
    if not init_data:
        return _json_response(
            {
                "status": "ok",
                "mode": "local",
                "authenticated": False,
            }
        )

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        return _json_response(
            {
                "status": "error",
                "mode": "telegram",
                "authenticated": False,
                "error": "bot_token_not_configured",
            },
            status=503,
        )

    try:
        validated = validate_telegram_init_data(init_data, token)
    except TelegramAuthError:
        return _json_response(
            {
                "status": "error",
                "mode": "telegram",
                "authenticated": False,
                "error": "invalid_init_data",
            },
            status=401,
        )

    user = build_safe_webapp_user(validated)
    if "id" not in user:
        return _json_response(
            {
                "status": "error",
                "mode": "telegram",
                "authenticated": False,
                "error": "invalid_init_data",
            },
            status=401,
        )

    return _json_response(
        {
            "status": "ok",
            "mode": "telegram",
            "authenticated": True,
            "user": user,
        }
    )


def _json_response(data: dict[str, Any], status: int = 200) -> web.Response:
    return web.json_response(data, status=status, dumps=_json_dumps)


def _json_dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False)
