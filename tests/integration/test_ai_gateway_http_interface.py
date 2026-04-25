import unittest

from fastapi.testclient import TestClient

from app.capabilities.ai_gateway import (
    AiGatewayAvailability,
    AiGatewayResponse,
    OutputMode,
    TokenUsage,
)
from app.interfaces.http.app import build_http_app


class FakeAiGateway:
    def __init__(self, availability: AiGatewayAvailability) -> None:
        self._availability = availability
        self.generated_profile: str | None = None

    def check_availability(self) -> AiGatewayAvailability:
        return self._availability

    def generate(self, request):
        self.generated_profile = str(request.capability_profile)
        return AiGatewayResponse(
            output_mode=OutputMode.TEXT,
            content="pong",
            usage=TokenUsage(input_tokens=1, output_tokens=1),
        )


class AiGatewayHttpInterfaceTest(unittest.TestCase):
    def test_availability_endpoint_returns_503_when_gateway_is_unavailable(
        self,
    ) -> None:
        client = TestClient(build_http_app())

        response = client.get("/ai-gateway/availability")

        self.assertEqual(503, response.status_code)
        self.assertEqual(
            {
                "component": "ai_gateway",
                "status": "unavailable",
                "configured": False,
                "reason": "AI gateway config path is not configured.",
            },
            response.json(),
        )

    def test_availability_endpoint_returns_200_when_gateway_is_available(self) -> None:
        app = build_http_app(
            ai_gateway_checker=FakeAiGateway(AiGatewayAvailability.available())
        )
        client = TestClient(app)

        response = client.get("/ai-gateway/availability")

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            {
                "component": "ai_gateway",
                "status": "available",
                "configured": True,
            },
            response.json(),
        )

    def test_generate_endpoint_returns_503_when_generation_service_is_not_configured(
        self,
    ) -> None:
        client = TestClient(build_http_app())

        response = client.post(
            "/ai-gateway/generate",
            json={
                "capability_profile": "smoke-test",
                "messages": [{"role": "user", "content": "ping"}],
                "output_mode": "text",
            },
        )

        self.assertEqual(503, response.status_code)
        self.assertEqual(
            {"detail": "AI gateway generation service is not configured."},
            response.json(),
        )

    def test_generate_endpoint_calls_ai_gateway_generate(self) -> None:
        gateway = FakeAiGateway(AiGatewayAvailability.available())
        app = build_http_app(ai_gateway_checker=gateway)
        client = TestClient(app)

        response = client.post(
            "/ai-gateway/generate",
            json={
                "capability_profile": "smoke-test",
                "messages": [{"role": "user", "content": "ping"}],
                "output_mode": "text",
            },
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual("smoke-test", gateway.generated_profile)
        self.assertEqual(
            {
                "output_mode": "text",
                "content": "pong",
                "structured_content": None,
                "usage": {
                    "input_tokens": 1,
                    "output_tokens": 1,
                    "total_tokens": 2,
                },
                "metadata": {},
            },
            response.json(),
        )


if __name__ == "__main__":
    unittest.main()
