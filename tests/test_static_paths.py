from backend_stub.main import create_app


def test_backend_registers_mini_app_static_paths() -> None:
    app = create_app()
    paths = {resource.canonical for resource in app.router.resources()}

    assert "/api/universities" in paths
    assert "/miniapp" in paths
    assert "/miniapp/" in paths
    assert "/miniapp/{asset}" in paths
    assert "/favicon.ico" in paths
