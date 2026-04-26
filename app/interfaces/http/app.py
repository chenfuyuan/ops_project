"""HTTP 应用聚合入口。

本模块只注册各协议 router，并为未装配依赖提供安全占位实现。
"""

from fastapi import FastAPI

from app.capabilities.ai_gateway import (
    AiGatewayAvailability,
    AiGatewayRequest,
    AiGatewayResponse,
)
from app.interfaces.http.ai_gateway import (
    AiGatewayHttpGateway,
    create_ai_gateway_router,
)
from app.interfaces.http.health import health_router
from app.interfaces.http.outline import (
    OutlineHttpService,
    UnavailableOutlineService,
    create_outline_router,
)


class UnavailableAiGatewayChecker:
    """HTTP app 默认使用的安全占位 checker，避免未装配时误报可用。"""

    def check_availability(self) -> AiGatewayAvailability:
        """返回未配置状态；正式运行时由 bootstrap 注入真实 checker。"""
        return AiGatewayAvailability.unavailable(
            configured=False,
            reason="AI gateway config path is not configured.",
        )

    def generate(self, request: AiGatewayRequest) -> AiGatewayResponse:
        """阻止未装配生成 service 时误触发模型调用。"""
        raise RuntimeError("AI gateway generation service is not configured.")


def build_http_app(
    *,
    ai_gateway_checker: AiGatewayHttpGateway | None = None,
    outline_service: OutlineHttpService | None = None,
) -> FastAPI:
    """构建 FastAPI app；具体业务和 capability 实现由 bootstrap 注入。"""
    app = FastAPI(title="Person Up Ops Project")
    app.include_router(health_router)
    app.include_router(
        create_ai_gateway_router(ai_gateway_checker or UnavailableAiGatewayChecker())
    )
    app.include_router(create_outline_router(outline_service or UnavailableOutlineService()))
    return app


app = build_http_app()
