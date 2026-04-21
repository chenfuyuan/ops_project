from fastapi import FastAPI

from app.interfaces.http.health import health_router


def build_http_app() -> FastAPI:
    app = FastAPI(title="Person Up Ops Project")
    app.include_router(health_router)
    return app


app = build_http_app()
