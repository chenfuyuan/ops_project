import logging

from app.capabilities.ai_gateway.config.repository import AiGatewayConfigRepository
from app.capabilities.ai_gateway.contracts.request import AiGatewayRequest
from app.capabilities.ai_gateway.contracts.response import AiGatewayResponse
from app.capabilities.ai_gateway.errors import AiGatewayConfigError
from app.capabilities.ai_gateway.providers.base import AiModelProvider

logger = logging.getLogger(__name__)


class AiGatewayService:
    """AI 网关内部编排层，负责 profile 解析、provider 选择和统一调用。"""

    def __init__(
        self,
        *,
        config_repository: AiGatewayConfigRepository,
        providers: dict[str, AiModelProvider],
    ) -> None:
        self._config_repository = config_repository
        self._providers = providers

    def generate(self, request: AiGatewayRequest) -> AiGatewayResponse:
        logger.info(
            "ai_gateway_request_started",
            extra={"profile": str(request.capability_profile), "output_mode": request.output_mode.value},
        )
        profile = self._config_repository.get_profile(request.capability_profile)
        provider_config = self._config_repository.get_provider(profile.provider)
        provider = self._providers.get(provider_config.kind)
        if provider is None:
            raise AiGatewayConfigError(
                "AI gateway provider kind is not registered",
                safe_context={"provider": provider_config.name, "kind": provider_config.kind},
            )
        api_key = self._config_repository.resolve_provider_api_key(provider_config.name)
        response = provider.generate(
            request=request,
            profile=profile,
            provider_config=provider_config,
            api_key=api_key,
        )
        logger.info(
            "ai_gateway_request_completed",
            extra={
                "profile": profile.name,
                "provider": provider_config.name,
                "output_mode": response.output_mode.value,
            },
        )
        return response
