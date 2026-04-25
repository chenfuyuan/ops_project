from typing import Protocol

from app.capabilities.ai_gateway.contracts.models import CapabilityProfileName
from app.capabilities.ai_gateway.config.models import (
    AiGatewayProfileConfig,
    AiGatewayProviderConfig,
)


class AiGatewayConfigRepository(Protocol):
    """AI 网关核心逻辑依赖的配置读取抽象。"""

    def get_profile(self, name: CapabilityProfileName) -> AiGatewayProfileConfig:
        """按中性 profile 名称读取模型能力配置。"""

    def get_provider(self, name: str) -> AiGatewayProviderConfig:
        """按 provider 名称读取外部模型连接配置。"""

    def resolve_provider_api_key(self, provider_name: str) -> str:
        """按 provider 名称解析运行时密钥。"""
