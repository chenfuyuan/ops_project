from fastapi import APIRouter

from app.interfaces.http.schemas.common import HealthResponse


def build_health_router(*, service_name: str) -> APIRouter:
    router = APIRouter()

    @router.get("/health", response_model=HealthResponse, tags=["system"])
    async def healthcheck() -> HealthResponse:
        return HealthResponse(status="ok", service=service_name)

    return router
