from typing import Protocol, runtime_checkable

from app.capabilities.ai_gateway.config.models import (
    AiGatewayProfileConfig,
    AiGatewayProviderConfig,
)
from app.capabilities.ai_gateway.contracts.request import AiGatewayRequest
from app.capabilities.ai_gateway.contracts.response import (
    AiGatewayAvailability,
    AiGatewayResponse,
)


@runtime_checkable
class AiGatewayAvailabilityProvider(Protocol):
    """AI 网关诊断流程依赖的可用性检查抽象。"""

    def check_availability(self) -> AiGatewayAvailability:
        """返回不含敏感信息的网关可用性结果。"""


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
