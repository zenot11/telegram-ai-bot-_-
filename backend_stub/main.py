import json
import os
from pathlib import Path
from typing import Any

from aiohttp import web
from dotenv import load_dotenv


load_dotenv()

DATA_PATH = Path(__file__).resolve().parent / "data" / "universities.json"

DIRECTION_SYNONYMS = {
    "IT": ("it", "айти", "информатика", "программирование", "информационные", "данные"),
    "психология": ("психолог", "психология"),
    "медицина": ("медицина", "мед", "лечебное", "врач"),
    "экономика": ("экономика", "эконом", "бизнес", "финансы", "менеджмент"),
    "педагогика": ("педагогика", "педагог", "учитель", "образование"),
    "юриспруденция": ("юриспруденция", "юрист", "право", "законы"),
    "инженерия": ("инженерия", "инженер", "техника", "машиностроение", "строительство"),
}


def load_universities() -> list[dict[str, Any]]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def normalize(text: str) -> str:
    return text.strip().lower().replace("ё", "е")


def normalize_type(value: str) -> str:
    normalized = normalize(value)
    if normalized in {"budget", "бюджет"} or "бюдж" in normalized:
        return "бюджет"
    if normalized in {"paid", "платное", "платно", "контракт"} or "плат" in normalized:
        return "платное"
    return normalized


def direction_matches(item: dict[str, Any], direction: str) -> bool:
    requested = normalize(direction)
    if not requested:
        return True

    values = [
        item.get("program", ""),
        item.get("direction", ""),
        " ".join(item.get("directions") or []),
    ]
    haystack = normalize(" ".join(values))

    requested_direction = canonical_direction(requested)
    item_direction = canonical_direction(haystack)
    if requested_direction and item_direction and requested_direction == item_direction:
        return True

    return requested in haystack or any(part and part in haystack for part in requested.split())


def canonical_direction(text: str) -> str | None:
    normalized = normalize(text)
    for direction, synonyms in DIRECTION_SYNONYMS.items():
        if normalized == normalize(direction):
            return direction
        if any(synonym in normalized for synonym in synonyms):
            return direction
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

    rows = load_universities()

    results = [
        item
        for item in rows
        if normalize(item.get("region", "")) == normalize(region)
        and int(item.get("min_score", 0)) <= score
        and normalize(item.get("type", "")) == education_type
        and direction_matches(item, direction)
    ]
    return web.json_response(results[:limit], dumps=_json_dumps)


def _json_dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False)


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/health", health)
    app.router.add_get("/api/universities", universities)
    return app


if __name__ == "__main__":
    port = int(os.getenv("BACKEND_PORT", "8000"))
    web.run_app(create_app(), host="0.0.0.0", port=port)
