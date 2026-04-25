import unittest

import httpx

from app.capabilities.ai_gateway import (
    AiGatewayRequest,
    CapabilityProfileName,
    OutputMode,
    ProviderCallError,
    ProviderTimeoutError,
)
from app.capabilities.ai_gateway.config import (
    AiGatewayProfileConfig,
    AiGatewayProviderConfig,
)
from app.capabilities.ai_gateway.providers.httpx_transport import HttpxJsonTransport
from app.capabilities.ai_gateway.providers.openai_compatible import (
    OpenAICompatibleProvider,
)


class AiGatewayOpenAICompatibleProviderIntegrationTest(unittest.TestCase):
    def test_provider_maps_request_and_response_through_local_http_transport(
        self,
    ) -> None:
        captured_requests: list[dict] = []

        def handler(request: httpx.Request) -> httpx.Response:
            captured_requests.append(
                {
                    "url": str(request.url),
                    "authorization": request.headers.get("Authorization"),
                    "json": dict(
                        request.read() and __import__("json").loads(request.content)
                    ),
                }
            )
            return httpx.Response(
                200,
                json={
                    "choices": [{"message": {"content": "集成响应"}}],
                    "usage": {"prompt_tokens": 3, "completion_tokens": 4},
                },
            )

        provider = OpenAICompatibleProvider(
            transport=HttpxJsonTransport(
                client=httpx.Client(transport=httpx.MockTransport(handler))
            )
        )

        response = provider.generate(
            request=self._request(),
            profile=self._profile(retry_attempts=0),
            provider_config=self._provider_config(),
            api_key="secret-value",
        )

        self.assertEqual("集成响应", response.content)
        self.assertEqual(7, response.usage.total_tokens)
        self.assertEqual("Bearer secret-value", captured_requests[0]["authorization"])
        self.assertEqual("gpt-compatible-small", captured_requests[0]["json"]["model"])

    def test_provider_converts_http_status_error(self) -> None:
        provider = OpenAICompatibleProvider(
            transport=HttpxJsonTransport(
                client=httpx.Client(
                    transport=httpx.MockTransport(
                        lambda request: httpx.Response(500, json={"error": "boom"})
                    )
                )
            )
        )

        with self.assertRaises(ProviderCallError):
            provider.generate(
                request=self._request(),
                profile=self._profile(retry_attempts=0),
                provider_config=self._provider_config(),
                api_key="secret-value",
            )

    def test_provider_converts_http_timeout(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.TimeoutException("slow")

        provider = OpenAICompatibleProvider(
            transport=HttpxJsonTransport(
                client=httpx.Client(transport=httpx.MockTransport(handler))
            )
        )

        with self.assertRaises(ProviderTimeoutError):
            provider.generate(
                request=self._request(),
                profile=self._profile(retry_attempts=0),
                provider_config=self._provider_config(),
                api_key="secret-value",
            )

    def _request(self) -> AiGatewayRequest:
        return AiGatewayRequest(
            capability_profile=CapabilityProfileName("balanced_text"),
            messages=[{"role": "user", "content": "写一段简介"}],
            output_mode=OutputMode.TEXT,
        )

    def _profile(self, retry_attempts: int) -> AiGatewayProfileConfig:
        return AiGatewayProfileConfig(
            name="balanced_text",
            provider="primary-openai-compatible",
            model="gpt-compatible-small",
            capability_tags=["text"],
            context_window=32_000,
            cost_tier="balanced",
            timeout_seconds=30,
            retry_attempts=retry_attempts,
        )

    def _provider_config(self) -> AiGatewayProviderConfig:
        return AiGatewayProviderConfig(
            name="primary-openai-compatible",
            kind="openai-compatible",
            base_url="https://example.test/v1",
            api_key_env="AI_GATEWAY_API_KEY",
        )


if __name__ == "__main__":
    unittest.main()
