from typing import Protocol, runtime_checkable

from app.capabilities.ai_gateway.config.models import (
    AiGatewayProfileConfig,
    AiGatewayProviderConfig,
)
from app.capabilities.ai_gateway.contracts.request import AiGatewayRequest
from app.capabilities.ai_gateway.contracts.response import AiGatewayResponse


@runtime_checkable
class AiModelProvider(Protocol):
    """AI 网关 service 依赖的 provider 抽象。"""

    def generate(
        self,
        *,
        request: AiGatewayRequest,
        profile: AiGatewayProfileConfig,
        provider_config: AiGatewayProviderConfig,
        api_key: str,
    ) -> AiGatewayResponse:
        """执行一次中性模型能力请求并返回统一响应。"""
