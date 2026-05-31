import json
import os
from pathlib import Path
from typing import Any

from aiohttp import web

from backend_stub.db import PostgresConfigError, close_pool, create_pool, is_postgres_enabled
from backend_stub.data_loader import DataLoadError, get_universities_data_path, load_universities
from backend_stub.favorites_api import setup_favorites_routes
from backend_stub.feedback_api import setup_feedback_routes
from backend_stub.university_repository import (
    count_json_universities,
    count_postgres_universities,
    direction_matches,
    fetch_postgres_universities,
    filter_json_universities,
    normalize,
    normalize_limit,
    normalize_type,
)
from backend_stub.webapp_session import setup_webapp_session_routes

MINI_APP_PATH = Path(__file__).resolve().parent.parent / "mini_app"
MINI_APP_ASSETS = {"styles.css", "app.js", "favicon.svg"}
UNIVERSITIES_KEY = web.AppKey("universities", list[dict[str, Any]])
DATA_PATH_KEY = web.AppKey("data_path", Path)
STORAGE_KEY = web.AppKey("storage", str)
DATA_SOURCE_KEY = web.AppKey("data_source", str)
DB_POOL_KEY = web.AppKey("db_pool", Any)


filter_universities = filter_json_universities


async def health(request: web.Request) -> web.Response:
    storage = request.app[STORAGE_KEY]
    data_source = request.app[DATA_SOURCE_KEY]
    if storage == "postgresql":
        pool = request.app.get(DB_POOL_KEY)
        if pool is None:
            return web.json_response(
                {
                    "status": "error",
                    "service": "backend_stub",
                    "storage": "postgresql",
                    "data_source": "postgresql",
                    "error": "postgres_pool_not_initialized",
                },
                status=503,
                dumps=_json_dumps,
            )
        try:
            count = await count_postgres_universities(pool)
        except Exception:
            return web.json_response(
                {
                    "status": "error",
                    "service": "backend_stub",
                    "storage": "postgresql",
                    "data_source": "postgresql",
                    "error": "postgres_health_check_failed",
                },
                status=503,
                dumps=_json_dumps,
            )
        return web.json_response(
            {
                "status": "ok",
                "service": "backend_stub",
                "storage": "postgresql",
                "data_source": data_source,
                "universities_count": count,
            },
            dumps=_json_dumps,
        )

    universities = request.app[UNIVERSITIES_KEY]
    return web.json_response(
        {
            "status": "ok",
            "service": "backend_stub",
            "storage": "json",
            "data_source": data_source,
            "universities_count": count_json_universities(universities),
        },
        dumps=_json_dumps,
    )


async def universities(request: web.Request) -> web.Response:
    region = request.query.get("region", "")
    direction = request.query.get("direction", "")
    education_type = normalize_type(request.query.get("type", ""))

    try:
        limit = normalize_limit(int(request.query.get("limit", "5")))
    except ValueError:
        limit = 5

    try:
        score = int(request.query.get("score", "0"))
    except ValueError:
        return web.json_response({"error": "score must be an integer"}, status=400)

    if request.app[STORAGE_KEY] == "postgresql":
        pool = request.app.get(DB_POOL_KEY)
        if pool is None:
            return web.json_response({"error": "postgres pool is not initialized"}, status=503)
        try:
            results = await fetch_postgres_universities(pool, region, score, direction, education_type, limit)
        except Exception:
            return web.json_response({"error": "postgres query failed"}, status=503)
    else:
        results = filter_universities(request.app[UNIVERSITIES_KEY], region, score, direction, education_type, limit)
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


def create_app(
    universities_data: list[dict[str, Any]] | None = None,
    favorites_storage: Any | None = None,
    use_postgres: bool | None = None,
) -> web.Application:
    data_path = get_universities_data_path()
    app = web.Application()
    postgres_enabled = is_postgres_enabled() if use_postgres is None else use_postgres
    storage = "postgresql" if postgres_enabled and universities_data is None else "json"

    if storage == "postgresql":
        app[UNIVERSITIES_KEY] = []
        app[DATA_SOURCE_KEY] = "postgresql"
        app.cleanup_ctx.append(postgres_lifecycle)
    else:
        universities_data = universities_data if universities_data is not None else load_universities(data_path)
        app[UNIVERSITIES_KEY] = universities_data
        try:
            data_source = str(data_path.relative_to(Path.cwd()))
        except ValueError:
            data_source = str(data_path)
        app[DATA_SOURCE_KEY] = data_source

    app[DATA_PATH_KEY] = data_path
    app[STORAGE_KEY] = storage
    app.router.add_get("/health", health)
    app.router.add_get("/api/universities", universities)
    setup_webapp_session_routes(app)
    setup_favorites_routes(app, favorites_storage)
    setup_feedback_routes(app)
    app.router.add_get("/miniapp", miniapp_index)
    app.router.add_get("/miniapp/", miniapp_index)
    app.router.add_get("/miniapp/{asset}", miniapp_asset)
    app.router.add_get("/favicon.ico", favicon)
    return app


async def postgres_lifecycle(app: web.Application):
    try:
        pool = await create_pool()
    except PostgresConfigError as error:
        raise RuntimeError(f"PostgreSQL storage is enabled but connection failed: {error}") from error

    app[DB_POOL_KEY] = pool
    try:
        yield
    finally:
        await close_pool(pool)


if __name__ == "__main__":
    port = int(os.getenv("BACKEND_PORT", "8000"))
    try:
        web.run_app(create_app(), host="0.0.0.0", port=port)
    except DataLoadError as error:
        raise SystemExit(f"Backend data error: {error}") from error
