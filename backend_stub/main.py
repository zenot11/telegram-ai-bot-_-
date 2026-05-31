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
    build_university_filters,
    count_json_universities,
    count_postgres_universities,
    direction_matches,
    fetch_admission_types_json,
    fetch_admission_types_postgres,
    fetch_cities_json,
    fetch_cities_postgres,
    fetch_directions_json,
    fetch_directions_postgres,
    fetch_postgres_universities,
    fetch_regions_json,
    fetch_regions_postgres,
    fetch_study_forms_json,
    fetch_study_forms_postgres,
    fetch_universities_json,
    fetch_universities_postgres,
    filter_json_universities,
    normalize,
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
FEATURES = [
    "universities",
    "regions",
    "cities",
    "directions",
    "study_forms",
    "admission_types",
    "filters",
    "sorting",
]


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
                    "features": FEATURES,
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
                    "features": FEATURES,
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
                "features": FEATURES,
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
            "features": FEATURES,
        },
        dumps=_json_dumps,
    )


async def universities(request: web.Request) -> web.Response:
    filters = build_university_filters(request.query)
    if request.app[STORAGE_KEY] == "postgresql":
        pool = request.app.get(DB_POOL_KEY)
        if pool is None:
            return web.json_response({"error": "postgres pool is not initialized"}, status=503)
        try:
            results = await fetch_universities_postgres(pool, filters)
        except Exception:
            return web.json_response({"error": "postgres query failed"}, status=503)
    else:
        results = fetch_universities_json(request.app[UNIVERSITIES_KEY], filters)
    return web.json_response(results, dumps=_json_dumps)


async def regions(request: web.Request) -> web.Response:
    if request.app[STORAGE_KEY] == "postgresql":
        items = await fetch_regions_postgres(request.app[DB_POOL_KEY])
    else:
        items = fetch_regions_json(request.app[UNIVERSITIES_KEY])
    return _directory_response(request, items)


async def cities(request: web.Request) -> web.Response:
    region = request.query.get("region", "")
    if request.app[STORAGE_KEY] == "postgresql":
        items = await fetch_cities_postgres(request.app[DB_POOL_KEY], region)
    else:
        items = fetch_cities_json(request.app[UNIVERSITIES_KEY], region)
    return _directory_response(request, items)


async def directions(request: web.Request) -> web.Response:
    filters = build_university_filters(request.query)
    if request.app[STORAGE_KEY] == "postgresql":
        items = await fetch_directions_postgres(request.app[DB_POOL_KEY], filters)
    else:
        items = fetch_directions_json(request.app[UNIVERSITIES_KEY], filters)
    return _directory_response(request, items)


async def study_forms(request: web.Request) -> web.Response:
    if request.app[STORAGE_KEY] == "postgresql":
        items = await fetch_study_forms_postgres(request.app[DB_POOL_KEY])
    else:
        items = fetch_study_forms_json(request.app[UNIVERSITIES_KEY])
    return _directory_response(request, items)


async def admission_types(request: web.Request) -> web.Response:
    if request.app[STORAGE_KEY] == "postgresql":
        items = await fetch_admission_types_postgres(request.app[DB_POOL_KEY])
    else:
        items = fetch_admission_types_json(request.app[UNIVERSITIES_KEY])
    return _directory_response(request, items)


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


def _directory_response(request: web.Request, items: list[str]) -> web.Response:
    return web.json_response(
        {
            "storage": request.app[STORAGE_KEY],
            "count": len(items),
            "items": items,
        },
        dumps=_json_dumps,
    )


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
    app.router.add_get("/api/regions", regions)
    app.router.add_get("/api/cities", cities)
    app.router.add_get("/api/directions", directions)
    app.router.add_get("/api/study-forms", study_forms)
    app.router.add_get("/api/admission-types", admission_types)
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
