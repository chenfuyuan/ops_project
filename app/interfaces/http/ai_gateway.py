from typing import Protocol

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.capabilities.ai_gateway import AiGatewayAvailability, AiGatewayRequest, AiGatewayResponse


class AiGatewayHttpGateway(Protocol):
    """HTTP 层依赖的 AI 网关入口，协议层只负责请求和响应映射。"""

    def check_availability(self) -> AiGatewayAvailability:
        """返回 AI 网关当前可用性，HTTP 层只负责映射为协议响应。"""

    def generate(self, request: AiGatewayRequest) -> AiGatewayResponse:
        """执行一次中性模型能力请求，并返回统一响应。"""


def create_ai_gateway_router(
    gateway: AiGatewayHttpGateway,
) -> APIRouter:
    """创建 AI 网关测试路由，并通过注入的 gateway 保持运行时装配在外部。"""
    router = APIRouter()

    @router.get("/ai-gateway/availability")
    def availability() -> JSONResponse:
        result = gateway.check_availability()
        status_code = 200 if result.status == "available" else 503
        return JSONResponse(
            status_code=status_code,
            content=result.model_dump(exclude_none=True),
        )

    @router.post("/ai-gateway/generate")
    def generate(request: AiGatewayRequest) -> JSONResponse:
        try:
            result = gateway.generate(request)
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return JSONResponse(content=result.model_dump(mode="json"))

    return router
