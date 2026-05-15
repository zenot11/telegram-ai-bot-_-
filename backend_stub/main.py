import json
import os
from pathlib import Path
from typing import Any

from aiohttp import web
from dotenv import load_dotenv

from telegram_bot.services.recommendation import AMBITIOUS_SCORE_MARGIN
from telegram_bot.services.validation import (
    education_type_label,
    normalize_direction,
    normalize_education_type,
    normalize_region,
    normalize_text,
)


load_dotenv()

DATA_PATH = Path(__file__).resolve().parent / "data" / "universities.json"
MINI_APP_PATH = Path(__file__).resolve().parent.parent / "mini_app"
MINI_APP_ASSETS = {"styles.css", "app.js", "favicon.svg"}


def load_universities() -> list[dict[str, Any]]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def normalize(text: str) -> str:
    return normalize_text(text)


def normalize_type(value: str) -> str:
    normalized = normalize_education_type(value)
    if normalized:
        return education_type_label(normalized)
    return normalize(value)


def direction_matches(item: dict[str, Any], direction: str) -> bool:
    requested = normalize_direction(direction)
    if not requested:
        return True

    values = [
        item.get("program", ""),
        item.get("direction", ""),
        " ".join(item.get("directions") or []),
    ]
    haystack = " ".join(values)
    requested_direction = normalize_direction(requested)
    item_direction = normalize_direction(haystack)
    if normalize(requested_direction) == normalize(item_direction):
        return True

    normalized_requested = normalize(requested)
    normalized_haystack = normalize(haystack)
    return normalized_requested in normalized_haystack or any(
        part and part in normalized_haystack for part in normalized_requested.split()
    )


def filter_universities(
    rows: list[dict[str, Any]],
    region: str,
    score: int,
    direction: str,
    education_type: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    normalized_type = normalize_type(education_type)
    safe_limit = max(1, min(limit, 20))

    results = [
        item
        for item in rows
        if normalize_region(item.get("region", "")) == normalize_region(region)
        and _min_score(item) is not None
        and (_min_score(item) or 0) <= score + AMBITIOUS_SCORE_MARGIN
        and normalize(item.get("type", "")) == normalized_type
        and direction_matches(item, direction)
    ]
    return results[:safe_limit]


def _min_score(item: dict[str, Any]) -> int | None:
    value = item.get("min_score")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


async def health(_: web.Request) -> web.Response:
    return web.Response(text="ok")


async def universities(request: web.Request) -> web.Response:
    region = request.query.get("region", "")
    direction = request.query.get("direction", "")
    education_type = normalize_type(request.query.get("type", ""))

    try:
        limit = int(request.query.get("limit", "5"))
    except ValueError:
        limit = 5
    limit = max(1, min(limit, 20))

    try:
        score = int(request.query.get("score", "0"))
    except ValueError:
        return web.json_response({"error": "score must be an integer"}, status=400)

    results = filter_universities(load_universities(), region, score, direction, education_type, limit)
    return web.json_response(results[:limit], dumps=_json_dumps)


async def miniapp_index(_: web.Request) -> web.FileResponse:
    return web.FileResponse(MINI_APP_PATH / "index.html")


async def miniapp_asset(request: web.Request) -> web.FileResponse:
    asset = request.match_info.get("asset", "")
    if asset not in MINI_APP_ASSETS:
        raise web.HTTPNotFound()
    return web.FileResponse(MINI_APP_PATH / asset)


async def favicon(_: web.Request) -> web.FileResponse:
    return web.FileResponse(MINI_APP_PATH / "favicon.svg")


def _json_dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False)


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/health", health)
    app.router.add_get("/api/universities", universities)
    app.router.add_get("/miniapp", miniapp_index)
    app.router.add_get("/miniapp/", miniapp_index)
    app.router.add_get("/miniapp/{asset}", miniapp_asset)
    app.router.add_get("/favicon.ico", favicon)
    return app


if __name__ == "__main__":
    port = int(os.getenv("BACKEND_PORT", "8000"))
    web.run_app(create_app(), host="0.0.0.0", port=port)
