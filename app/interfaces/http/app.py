from fastapi import FastAPI

from app.interfaces.http.middleware.request_context import register_request_context_middleware
from app.interfaces.http.routes.health import build_health_router


def configure_http_interface(app: FastAPI, *, service_name: str) -> None:
    register_request_context_middleware(app)
    app.include_router(build_health_router(service_name=service_name))
