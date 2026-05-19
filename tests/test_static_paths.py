import asyncio
import json

from backend_stub.main import UNIVERSITIES_KEY, create_app, health


def test_backend_registers_mini_app_static_paths() -> None:
    app = create_app()
    paths = {resource.canonical for resource in app.router.resources()}

    assert "/api/universities" in paths
    assert "/api/favorites" in paths
    assert "/api/favorites/add" in paths
    assert "/api/favorites/remove" in paths
    assert "/api/favorites/clear" in paths
    assert "/api/favorites/sync" in paths
    assert "/miniapp" in paths
    assert "/miniapp/" in paths
    assert "/miniapp/{asset}" in paths
    assert "/favicon.ico" in paths


def test_health_response_contains_universities_count() -> None:
    app = create_app()

    class Request:
        pass

    request = Request()
    request.app = app
    response = asyncio.run(health(request))
    payload = json.loads(response.text)

    assert payload["status"] == "ok"
    assert payload["service"] == "backend_stub"
    assert payload["universities_count"] == len(app[UNIVERSITIES_KEY])
    assert payload["universities_count"] > 0
