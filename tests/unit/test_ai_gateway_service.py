import unittest

from app.capabilities.ai_gateway import (
    AiGatewayConfigError,
    AiGatewayFacade,
    AiGatewayRequest,
    AiGatewayResponse,
    CapabilityProfileName,
    OutputMode,
    TokenUsage,
)
from app.capabilities.ai_gateway.config import AiGatewayProfileConfig, AiGatewayProviderConfig
from app.capabilities.ai_gateway.service import AiGatewayService


class FakeRepository:
    def __init__(self) -> None:
        self.profile = AiGatewayProfileConfig(
            name="balanced_text",
            provider="primary-openai-compatible",
            model="gpt-compatible-small",
            capability_tags=["text"],
            context_window=32_000,
            cost_tier="balanced",
            timeout_seconds=30,
            retry_attempts=1,
        )
        self.provider = AiGatewayProviderConfig(
            name="primary-openai-compatible",
            kind="openai-compatible",
            base_url="https://example.test/v1",
            api_key_env="AI_GATEWAY_API_KEY",
        )
        self.resolved_provider_name: str | None = None

    def get_profile(self, name: CapabilityProfileName) -> AiGatewayProfileConfig:
        return self.profile

    def get_provider(self, name: str) -> AiGatewayProviderConfig:
        return self.provider

    def resolve_provider_api_key(self, provider_name: str) -> str:
        self.resolved_provider_name = provider_name
        return "secret-value"


class FakeProvider:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def generate(self, *, request, profile, provider_config, api_key):
        self.calls.append(
            {
                "request": request,
                "profile": profile,
                "provider_config": provider_config,
                "api_key": api_key,
            }
        )
        return AiGatewayResponse(
            output_mode=request.output_mode,
            content="生成文本",
            usage=TokenUsage(input_tokens=1, output_tokens=2),
            metadata={"profile": profile.name, "provider": provider_config.kind},
        )


class AiGatewayServiceTest(unittest.TestCase):
    def test_service_resolves_profile_selects_provider_and_generates(self) -> None:
        repository = FakeRepository()
        provider = FakeProvider()
        service = AiGatewayService(
            config_repository=repository,
            providers={"openai-compatible": provider},
        )

        response = service.generate(self._request())

        self.assertEqual("生成文本", response.content)
        self.assertEqual("primary-openai-compatible", repository.resolved_provider_name)
        self.assertEqual("secret-value", provider.calls[0]["api_key"])
        self.assertEqual("gpt-compatible-small", provider.calls[0]["profile"].model)

    def test_service_rejects_unknown_provider_kind(self) -> None:
        repository = FakeRepository()
        repository.provider = repository.provider.model_copy(update={"kind": "missing-provider"})
        service = AiGatewayService(config_repository=repository, providers={})

        with self.assertRaises(AiGatewayConfigError):
            service.generate(self._request())

    def test_facade_delegates_to_service(self) -> None:
        service = AiGatewayService(
            config_repository=FakeRepository(),
            providers={"openai-compatible": FakeProvider()},
        )
        facade = AiGatewayFacade(service=service)

        response = facade.generate(self._request())

        self.assertEqual("生成文本", response.content)

    def _request(self) -> AiGatewayRequest:
        return AiGatewayRequest(
            capability_profile=CapabilityProfileName("balanced_text"),
            messages=[{"role": "user", "content": "写一段简介"}],
            output_mode=OutputMode.TEXT,
        )


if __name__ == "__main__":
    unittest.main()
