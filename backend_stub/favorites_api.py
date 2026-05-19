import json
import os
from typing import Any

from aiohttp import web

from backend_stub.telegram_auth import (
    TelegramAuthError,
    extract_telegram_user_id,
    validate_telegram_init_data,
)
from telegram_bot.storage.user_data import UserDataStorage, user_storage


FAVORITES_STORAGE_KEY = web.AppKey("favorites_storage", UserDataStorage)
INIT_DATA_HEADER = "X-Telegram-Init-Data"


def setup_favorites_routes(app: web.Application, storage: UserDataStorage | None = None) -> None:
    app[FAVORITES_STORAGE_KEY] = storage or user_storage
    app.router.add_get("/api/favorites", get_favorites)
    app.router.add_post("/api/favorites/add", add_favorite)
    app.router.add_post("/api/favorites/remove", remove_favorite)
    app.router.add_post("/api/favorites/clear", clear_favorites)
    app.router.add_post("/api/favorites/sync", sync_favorites)


async def get_favorites(request: web.Request) -> web.Response:
    telegram_id = _telegram_id_from_request(request)
    return _favorites_response(request, telegram_id)


async def add_favorite(request: web.Request) -> web.Response:
    telegram_id = _telegram_id_from_request(request)
    body = await _read_json_body(request)
    item = body.get("item")
    if not isinstance(item, dict):
        return _json_error("item must be object", status=400)

    request.app[FAVORITES_STORAGE_KEY].add_favorite(telegram_id, item)
    return _favorites_response(request, telegram_id)


async def remove_favorite(request: web.Request) -> web.Response:
    telegram_id = _telegram_id_from_request(request)
    body = await _read_json_body(request)
    key = body.get("key")
    item = body.get("item")

    if isinstance(key, str) and key.strip():
        request.app[FAVORITES_STORAGE_KEY].remove_favorite_by_key(telegram_id, key)
    elif isinstance(item, dict):
        request.app[FAVORITES_STORAGE_KEY].remove_favorite_by_key(
            telegram_id,
            request.app[FAVORITES_STORAGE_KEY].favorite_key(item),
        )
    else:
        return _json_error("key or item is required", status=400)

    return _favorites_response(request, telegram_id)


async def clear_favorites(request: web.Request) -> web.Response:
    telegram_id = _telegram_id_from_request(request)
    request.app[FAVORITES_STORAGE_KEY].clear_favorites(telegram_id)
    return _favorites_response(request, telegram_id)


async def sync_favorites(request: web.Request) -> web.Response:
    telegram_id = _telegram_id_from_request(request)
    body = await _read_json_body(request)
    local_favorites = body.get("local_favorites", [])
    if not isinstance(local_favorites, list):
        return _json_error("local_favorites must be list", status=400)

    merged = request.app[FAVORITES_STORAGE_KEY].merge_favorites(
        telegram_id,
        [item for item in local_favorites if isinstance(item, dict)],
    )
    return _json_response({"status": "ok", "mode": "telegram", "favorites": merged})


def favorite_key(item: dict[str, Any]) -> str:
    return UserDataStorage.favorite_key(item)


def _telegram_id_from_request(request: web.Request) -> int:
    init_data = request.headers.get(INIT_DATA_HEADER, "")
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    try:
        validated = validate_telegram_init_data(init_data, token)
    except TelegramAuthError as error:
        raise web.HTTPUnauthorized(
            text=_json_dumps({"status": "error", "error": "unauthorized", "detail": str(error)}),
            content_type="application/json",
        ) from error

    telegram_id = extract_telegram_user_id(validated)
    if telegram_id is None:
        raise web.HTTPUnauthorized(
            text=_json_dumps({"status": "error", "error": "unauthorized", "detail": "user id is missing"}),
            content_type="application/json",
        )
    return telegram_id


async def _read_json_body(request: web.Request) -> dict[str, Any]:
    try:
        body = await request.json()
    except json.JSONDecodeError as error:
        raise web.HTTPBadRequest(
            text=_json_dumps({"status": "error", "error": "invalid json"}),
            content_type="application/json",
        ) from error
    return body if isinstance(body, dict) else {}


def _favorites_response(request: web.Request, telegram_id: int) -> web.Response:
    favorites = request.app[FAVORITES_STORAGE_KEY].get_favorites(telegram_id)
    return _json_response({"status": "ok", "mode": "telegram", "favorites": favorites})


def _json_error(message: str, status: int) -> web.Response:
    return _json_response({"status": "error", "error": message}, status=status)


def _json_response(data: dict[str, Any], status: int = 200) -> web.Response:
    return web.json_response(data, status=status, dumps=_json_dumps)


def _json_dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False)
