import unittest

from app.capabilities.ai_gateway import (
    AiGatewayRequest,
    CapabilityProfileName,
    MessageRole,
    OutputMode,
    ProviderCallError,
    ProviderResponseError,
    ProviderTimeoutError,
    StructuredOutputConstraint,
)
from app.capabilities.ai_gateway.config import (
    AiGatewayProfileConfig,
    AiGatewayProviderConfig,
)
from app.capabilities.ai_gateway.providers import (
    AiModelProvider,
    OpenAICompatibleProvider,
)


class FakeHttpTransport:
    def __init__(self, responses: list[dict | Exception]) -> None:
        self.responses = responses
        self.requests: list[dict] = []

    def post_json(
        self, *, url: str, headers: dict, payload: dict, timeout: float
    ) -> dict:
        self.requests.append(
            {"url": url, "headers": headers, "payload": payload, "timeout": timeout}
        )
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


class AiGatewayProviderTest(unittest.TestCase):
    def test_openai_compatible_provider_maps_text_request_and_response(self) -> None:
        transport = FakeHttpTransport(
            [
                {
                    "choices": [{"message": {"content": "生成文本"}}],
                    "usage": {"prompt_tokens": 10, "completion_tokens": 20},
                    "id": "chatcmpl-1",
                }
            ]
        )
        provider = OpenAICompatibleProvider(transport=transport)

        response = provider.generate(
            request=AiGatewayRequest(
                capability_profile=CapabilityProfileName("balanced_text"),
                messages=[{"role": MessageRole.USER, "content": "写一段简介"}],
                output_mode=OutputMode.TEXT,
            ),
            profile=self._profile(retry_attempts=0),
            provider_config=self._provider_config(),
            api_key="secret-value",
        )

        self.assertEqual("生成文本", response.content)
        self.assertEqual(30, response.usage.total_tokens)
        self.assertEqual("chatcmpl-1", response.metadata["provider_response_id"])
        sent = transport.requests[0]
        self.assertEqual("https://example.test/v1/chat/completions", sent["url"])
        self.assertEqual("Bearer secret-value", sent["headers"]["Authorization"])
        self.assertEqual("gpt-compatible-small", sent["payload"]["model"])
        self.assertEqual("user", sent["payload"]["messages"][0]["role"])

    def test_openai_compatible_provider_maps_structured_output_request(self) -> None:
        transport = FakeHttpTransport(
            [
                {
                    "choices": [{"message": {"content": '{"summary":"摘要"}'}}],
                    "usage": {"prompt_tokens": 5, "completion_tokens": 8},
                }
            ]
        )
        provider = OpenAICompatibleProvider(transport=transport)

        response = provider.generate(
            request=AiGatewayRequest(
                capability_profile=CapabilityProfileName("long_context_json"),
                messages=[{"role": "user", "content": "总结"}],
                output_mode=OutputMode.STRUCTURED,
                structured_output=StructuredOutputConstraint(
                    name="generic_summary",
                    schema={
                        "type": "object",
                        "properties": {"summary": {"type": "string"}},
                    },
                ),
            ),
            profile=self._profile(name="long_context_json", retry_attempts=0),
            provider_config=self._provider_config(),
            api_key="secret-value",
        )

        payload = transport.requests[0]["payload"]
        self.assertEqual("json_schema", payload["response_format"]["type"])
        self.assertEqual(
            "generic_summary", payload["response_format"]["json_schema"]["name"]
        )
        self.assertEqual({"summary": "摘要"}, response.structured_content)

    def test_openai_compatible_provider_converts_http_error(self) -> None:
        provider = OpenAICompatibleProvider(
            transport=FakeHttpTransport([RuntimeError("500 boom")])
        )

        with self.assertRaises(ProviderCallError):
            provider.generate(
                request=self._text_request(),
                profile=self._profile(retry_attempts=0),
                provider_config=self._provider_config(),
                api_key="secret-value",
            )

    def test_openai_compatible_provider_converts_timeout(self) -> None:
        provider = OpenAICompatibleProvider(
            transport=FakeHttpTransport([TimeoutError("slow")])
        )

        with self.assertRaises(ProviderTimeoutError):
            provider.generate(
                request=self._text_request(),
                profile=self._profile(retry_attempts=0),
                provider_config=self._provider_config(),
                api_key="secret-value",
            )

    def test_openai_compatible_provider_converts_unexpected_response(self) -> None:
        provider = OpenAICompatibleProvider(
            transport=FakeHttpTransport([{"choices": []}])
        )

        with self.assertRaises(ProviderResponseError):
            provider.generate(
                request=self._text_request(),
                profile=self._profile(retry_attempts=0),
                provider_config=self._provider_config(),
                api_key="secret-value",
            )

    def test_openai_compatible_provider_retries_recoverable_failure(self) -> None:
        transport = FakeHttpTransport(
            [
                RuntimeError("temporary"),
                {
                    "choices": [{"message": {"content": "重试成功"}}],
                    "usage": {"prompt_tokens": 1, "completion_tokens": 2},
                },
            ]
        )
        provider = OpenAICompatibleProvider(transport=transport)

        response = provider.generate(
            request=self._text_request(),
            profile=self._profile(retry_attempts=1),
            provider_config=self._provider_config(),
            api_key="secret-value",
        )

        self.assertEqual("重试成功", response.content)
        self.assertEqual(2, len(transport.requests))

    def test_provider_implements_base_protocol(self) -> None:
        provider = OpenAICompatibleProvider(transport=FakeHttpTransport([]))

        self.assertIsInstance(provider, AiModelProvider)

    def _text_request(self) -> AiGatewayRequest:
        return AiGatewayRequest(
            capability_profile=CapabilityProfileName("balanced_text"),
            messages=[{"role": "user", "content": "写一段简介"}],
            output_mode=OutputMode.TEXT,
        )

    def _profile(
        self, name: str = "balanced_text", retry_attempts: int = 0
    ) -> AiGatewayProfileConfig:
        return AiGatewayProfileConfig(
            name=name,
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
