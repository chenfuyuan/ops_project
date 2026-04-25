import unittest

from app.capabilities.ai_gateway import (
    AiGatewayRequest,
    CapabilityProfileName,
    OutputMode,
    TokenUsage,
)
from app.capabilities.ai_gateway.config import (
    AiGatewayProfileConfig,
    AiGatewayProviderConfig,
)
from app.capabilities.ai_gateway.contracts.response import AiGatewayResponse
from app.capabilities.ai_gateway.service import AiGatewayService


class FakeRepository:
    def get_profile(self, name):
        return AiGatewayProfileConfig(
            name="balanced_text",
            provider="primary-openai-compatible",
            model="gpt-compatible-small",
            capability_tags=["text"],
            context_window=32_000,
            cost_tier="balanced",
            timeout_seconds=30,
            retry_attempts=0,
        )

    def get_provider(self, name):
        return AiGatewayProviderConfig(
            name="primary-openai-compatible",
            kind="openai-compatible",
            base_url="https://example.test/v1",
            api_key_env="AI_GATEWAY_API_KEY",
        )

    def resolve_provider_api_key(self, provider_name):
        return "secret-api-key"


class FakeProvider:
    def generate(self, *, request, profile, provider_config, api_key):
        return AiGatewayResponse(
            output_mode=request.output_mode,
            content="完整模型输出不应进入日志",
            usage=TokenUsage(input_tokens=1, output_tokens=2),
        )


class AiGatewayLoggingTest(unittest.TestCase):
    def test_service_logs_safe_context_without_prompt_or_secret(self) -> None:
        service = AiGatewayService(
            config_repository=FakeRepository(),
            providers={"openai-compatible": FakeProvider()},
        )

        with self.assertLogs(
            "app.capabilities.ai_gateway.service", level="INFO"
        ) as logs:
            service.generate(
                AiGatewayRequest(
                    capability_profile=CapabilityProfileName("balanced_text"),
                    messages=[{"role": "user", "content": "完整 prompt 不应进入日志"}],
                    output_mode=OutputMode.TEXT,
                )
            )

        messages = [record.getMessage() for record in logs.records]
        record_fields = [record.__dict__ for record in logs.records]
        serialized_records = str(record_fields)
        self.assertIn("ai_gateway_request_started", messages)
        self.assertIn("ai_gateway_request_completed", messages)
        self.assertTrue(
            any(fields.get("profile") == "balanced_text" for fields in record_fields)
        )
        self.assertNotIn("secret-api-key", serialized_records)
        self.assertNotIn("完整 prompt 不应进入日志", serialized_records)
        self.assertNotIn("完整模型输出不应进入日志", serialized_records)


if __name__ == "__main__":
    unittest.main()
