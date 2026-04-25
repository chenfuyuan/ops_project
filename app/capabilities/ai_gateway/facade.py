from app.capabilities.ai_gateway.contracts.request import AiGatewayRequest
from app.capabilities.ai_gateway.contracts.response import AiGatewayResponse
from app.capabilities.ai_gateway.service import AiGatewayService


class AiGatewayFacade:
    """AI 网关对外稳定入口，屏蔽内部 service、配置和 provider 细节。"""

    def __init__(self, *, service: AiGatewayService) -> None:
        self._service = service

    def generate(self, request: AiGatewayRequest) -> AiGatewayResponse:
        """通过统一 AI 网关入口执行一次模型能力请求。"""
        return self._service.generate(request)
