from app.capabilities.ai_gateway.contracts.request import AiGatewayRequest
from app.capabilities.ai_gateway.contracts.response import (
    AiGatewayAvailability,
    AiGatewayResponse,
)
from app.capabilities.ai_gateway.providers.base import AiGatewayAvailabilityProvider
from app.capabilities.ai_gateway.service import AiGatewayService


class AiGatewayFacade:
    """AI 网关对外稳定入口，屏蔽内部 service、配置和 provider 细节。"""

    def __init__(
        self,
        *,
        service: AiGatewayService | None = None,
        availability_provider: AiGatewayAvailabilityProvider | None = None,
    ) -> None:
        self._service = service
        self._availability_provider = availability_provider

    def generate(self, request: AiGatewayRequest) -> AiGatewayResponse:
        """通过统一 AI 网关入口执行一次模型能力请求。"""
        if self._service is None:
            raise RuntimeError("AI gateway generation service is not configured")
        return self._service.generate(request)

    def check_availability(self) -> AiGatewayAvailability:
        """通过运行时装配的 provider 检查 AI 网关是否可用。"""
        if self._availability_provider is None:
            return AiGatewayAvailability.unavailable(
                configured=False,
                reason="AI gateway availability provider is not configured.",
            )
        return self._availability_provider.check_availability()
