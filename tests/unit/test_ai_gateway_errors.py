import unittest

from app.capabilities.ai_gateway import (
    AiGatewayConfigError,
    AiGatewayError,
    ProviderCallError,
    ProviderResponseError,
    ProviderTimeoutError,
    StructuredOutputError,
)


class AiGatewayErrorsTest(unittest.TestCase):
    def test_errors_expose_stable_code_and_safe_context(self) -> None:
        error = ProviderCallError(
            "provider failed",
            code="provider_call_failed",
            safe_context={"profile": "balanced_text", "provider": "openai-compatible"},
        )

        self.assertEqual("provider_call_failed", error.code)
        self.assertEqual("balanced_text", error.safe_context["profile"])
        self.assertNotIn("api_key", error.safe_context)
        self.assertIn("provider_call_failed", str(error))

    def test_specific_errors_have_default_codes(self) -> None:
        self.assertEqual("ai_gateway_config_error", AiGatewayConfigError("missing").code)
        self.assertEqual("provider_timeout", ProviderTimeoutError("timeout").code)
        self.assertEqual("provider_response_error", ProviderResponseError("bad response").code)
        self.assertEqual("structured_output_error", StructuredOutputError("bad json").code)

    def test_error_hierarchy_is_stable(self) -> None:
        self.assertIsInstance(AiGatewayConfigError("missing"), AiGatewayError)
        self.assertIsInstance(ProviderTimeoutError("timeout"), ProviderCallError)
        self.assertIsInstance(ProviderResponseError("bad response"), ProviderCallError)
        self.assertIsInstance(StructuredOutputError("bad json"), AiGatewayError)


if __name__ == "__main__":
    unittest.main()
