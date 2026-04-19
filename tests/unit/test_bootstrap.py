from app.bootstrap.startup import create_app


def test_create_app_registers_health_route_without_database_configuration(
    monkeypatch,
) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    app = create_app()
    route_paths = {route.path for route in app.routes}

    assert "/health" in route_paths
