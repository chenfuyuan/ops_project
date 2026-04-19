from fastapi import FastAPI

from app.bootstrap.container import AppContainer
from app.bootstrap.module_registry import ModuleRegistry
from app.interfaces.http.app import configure_http_interface


def wire_application(
    *,
    container: AppContainer,
    registry: ModuleRegistry,
) -> FastAPI:
    app = FastAPI(title=container.settings.service_name)
    app.state.container = container
    app.state.module_registry = registry

    configure_http_interface(app, service_name=container.settings.service_name)
    return app
