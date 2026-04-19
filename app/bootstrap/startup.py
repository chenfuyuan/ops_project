from fastapi import FastAPI

from app.bootstrap.container import build_container
from app.bootstrap.module_registry import create_module_registry
from app.bootstrap.wiring import wire_application


def create_app() -> FastAPI:
    container = build_container()
    registry = create_module_registry()
    return wire_application(container=container, registry=registry)
