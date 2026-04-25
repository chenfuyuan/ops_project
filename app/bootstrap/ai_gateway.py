import json
import os
from pathlib import Path
from pydantic import ValidationError

from app.capabilities.ai_gateway import AiGatewayFacade
from app.capabilities.ai_gateway.config import FileAiGatewayConfigRepository
from app.capabilities.ai_gateway.errors import AiGatewayConfigError
from app.capabilities.ai_gateway.providers.http_provider import HttpAiGatewayAvailabilityProvider
from app.capabilities.ai_gateway.providers.unconfigured_provider import (
    StaticUnavailableAiGatewayProvider,
    UnconfiguredAiGatewayProvider,
)
from app.capabilities.ai_gateway.service import AiGatewayService

_CONFIGURATION_EXCEPTIONS = (
    AiGatewayConfigError,
    OSError,
    UnicodeDecodeError,
    json.JSONDecodeError,
    ValidationError,
)


def create_ai_gateway_facade(config_path: Path | None = None) -> AiGatewayFacade:
    """装配 AI 网关 facade、配置 repository、生成 provider 和可用性 provider。"""
    from app.capabilities.ai_gateway.providers.openai_compatible import (
        OpenAICompatibleProvider,
    )
    from app.capabilities.ai_gateway.providers.urllib_transport import UrllibJsonTransport

    resolved_config_path = config_path or _default_config_path()
    if resolved_config_path is None:
        return AiGatewayFacade(availability_provider=UnconfiguredAiGatewayProvider())

    try:
        repository = FileAiGatewayConfigRepository.from_file(resolved_config_path)
        provider_config = repository.first_provider()
        api_key = repository.resolve_provider_api_key(provider_config.name)
    except _CONFIGURATION_EXCEPTIONS:
        return AiGatewayFacade(
            availability_provider=StaticUnavailableAiGatewayProvider(
                configured=True,
                reason="AI gateway config could not be loaded.",
            )
        )

    service = AiGatewayService(
        config_repository=repository,
        providers={
            "openai-compatible": OpenAICompatibleProvider(
                transport=UrllibJsonTransport()
            )
        },
    )
    return AiGatewayFacade(
        service=service,
        availability_provider=HttpAiGatewayAvailabilityProvider(
            base_url=provider_config.base_url,
            health_path="/health",
            timeout_seconds=5.0,
            api_key=api_key,
        ),
    )


def create_ai_gateway_availability_facade(
    config_path: Path | None = None,
) -> AiGatewayFacade:
    """使用既有 AI 网关配置装配可用性检查入口。"""
    return create_ai_gateway_facade(config_path)


def _default_config_path() -> Path | None:
    raw_path = os.environ.get("AI_GATEWAY_CONFIG_PATH")
    if not raw_path:
        return None
    return Path(raw_path)
