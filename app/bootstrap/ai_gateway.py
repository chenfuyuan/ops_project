import os
from pathlib import Path

from app.capabilities.ai_gateway import AiGatewayFacade
from app.capabilities.ai_gateway.config import FileAiGatewayConfigRepository
from app.capabilities.ai_gateway.providers import OpenAICompatibleProvider
from app.capabilities.ai_gateway.providers.httpx_transport import HttpxJsonTransport
from app.capabilities.ai_gateway.service import AiGatewayService


def create_ai_gateway_facade(config_path: Path | None = None) -> AiGatewayFacade:
    """装配 AI 网关 facade、配置 repository 和 OpenAI-compatible provider。"""
    resolved_config_path = config_path or Path(os.environ["AI_GATEWAY_CONFIG_PATH"])
    repository = FileAiGatewayConfigRepository.from_file(resolved_config_path)
    service = AiGatewayService(
        config_repository=repository,
        providers={"openai-compatible": OpenAICompatibleProvider(transport=HttpxJsonTransport())},
    )
    return AiGatewayFacade(service=service)
