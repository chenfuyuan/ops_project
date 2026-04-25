import unittest

from pydantic import ValidationError

from app.capabilities.ai_gateway import (
    AiGatewayRequest,
    AiGatewayResponse,
    CapabilityProfileName,
    MessageRole,
    OutputMode,
    StructuredOutputConstraint,
    TokenUsage,
)


class AiGatewayContractsTest(unittest.TestCase):
    def test_request_accepts_text_generation_messages(self) -> None:
        request = AiGatewayRequest(
            capability_profile=CapabilityProfileName("balanced_text"),
            messages=[{"role": MessageRole.USER, "content": "写一段简介"}],
            output_mode=OutputMode.TEXT,
        )

        self.assertEqual("balanced_text", request.capability_profile)
        self.assertEqual(OutputMode.TEXT, request.output_mode)
        self.assertEqual(MessageRole.USER, request.messages[0].role)
        self.assertEqual("写一段简介", request.messages[0].content)
        self.assertIsNone(request.structured_output)

    def test_request_accepts_neutral_structured_output_constraint(self) -> None:
        constraint = StructuredOutputConstraint(
            name="generic_summary",
            schema={
                "type": "object",
                "properties": {"summary": {"type": "string"}},
                "required": ["summary"],
            },
        )
        request = AiGatewayRequest(
            capability_profile=CapabilityProfileName("long_context_json"),
            messages=[{"role": "user", "content": "总结内容"}],
            output_mode=OutputMode.STRUCTURED,
            structured_output=constraint,
            metadata={"request_id": "req-1"},
        )

        self.assertEqual(OutputMode.STRUCTURED, request.output_mode)
        self.assertEqual("generic_summary", request.structured_output.name)
        self.assertEqual("object", request.structured_output.json_schema["type"])
        self.assertEqual("req-1", request.metadata["request_id"])

    def test_request_rejects_empty_messages(self) -> None:
        with self.assertRaises(ValidationError):
            AiGatewayRequest(
                capability_profile=CapabilityProfileName("balanced_text"),
                messages=[],
                output_mode=OutputMode.TEXT,
            )

    def test_structured_mode_requires_structured_constraint(self) -> None:
        with self.assertRaises(ValidationError):
            AiGatewayRequest(
                capability_profile=CapabilityProfileName("long_context_json"),
                messages=[{"role": "user", "content": "总结内容"}],
                output_mode=OutputMode.STRUCTURED,
            )

    def test_profile_name_rejects_implementation_details(self) -> None:
        with self.assertRaises(ValidationError):
            AiGatewayRequest(
                capability_profile=CapabilityProfileName("provider_model_selector"),
                messages=[{"role": "user", "content": "生成内容"}],
                output_mode=OutputMode.TEXT,
            )

    def test_response_contains_text_usage_and_neutral_metadata(self) -> None:
        response = AiGatewayResponse(
            output_mode=OutputMode.TEXT,
            content="生成文本",
            usage=TokenUsage(input_tokens=10, output_tokens=20),
            metadata={"profile": "balanced_text", "provider": "openai-compatible"},
        )

        self.assertEqual("生成文本", response.content)
        self.assertIsNone(response.structured_content)
        self.assertEqual(30, response.usage.total_tokens)
        self.assertEqual("balanced_text", response.metadata["profile"])

    def test_response_contains_structured_content(self) -> None:
        response = AiGatewayResponse(
            output_mode=OutputMode.STRUCTURED,
            structured_content={"summary": "摘要"},
            usage=TokenUsage(input_tokens=5, output_tokens=8),
        )

        self.assertIsNone(response.content)
        self.assertEqual({"summary": "摘要"}, response.structured_content)
        self.assertEqual(13, response.usage.total_tokens)


if __name__ == "__main__":
    unittest.main()
