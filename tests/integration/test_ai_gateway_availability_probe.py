from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import unittest

from app.capabilities.ai_gateway.providers.http_provider import HttpAiGatewayAvailabilityProvider


class HealthHandler(BaseHTTPRequestHandler):
    status_code = 200
    authorization_header = None

    def do_GET(self) -> None:
        type(self).authorization_header = self.headers.get("Authorization")
        self.send_response(type(self).status_code)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, format: str, *args: object) -> None:
        return None


class LocalHealthServer:
    def __init__(self, status_code: int) -> None:
        HealthHandler.status_code = status_code
        HealthHandler.authorization_header = None
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), HealthHandler)
        self._thread = Thread(target=self._server.serve_forever, daemon=True)

    @property
    def base_url(self) -> str:
        host, port = self._server.server_address
        return f"http://{host}:{port}"

    @property
    def authorization_header(self) -> str | None:
        return HealthHandler.authorization_header

    def __enter__(self) -> "LocalHealthServer":
        self._thread.start()
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=2)


class AiGatewayAvailabilityProbeTest(unittest.TestCase):
    def test_http_provider_reports_available_when_health_endpoint_returns_success(self) -> None:
        with LocalHealthServer(200) as server:
            provider = HttpAiGatewayAvailabilityProvider(
                base_url=server.base_url,
                health_path="/health",
                timeout_seconds=2,
                api_key="test-token",
            )

            result = provider.check_availability()

        self.assertEqual("available", result.status)
        self.assertTrue(result.configured)
        self.assertIsNone(result.reason)
        self.assertEqual("Bearer test-token", server.authorization_header)

    def test_http_provider_reports_unavailable_when_health_endpoint_fails(self) -> None:
        with LocalHealthServer(500) as server:
            provider = HttpAiGatewayAvailabilityProvider(
                base_url=server.base_url,
                health_path="/health",
                timeout_seconds=2,
                api_key=None,
            )

            result = provider.check_availability()

        self.assertEqual("unavailable", result.status)
        self.assertTrue(result.configured)
        self.assertEqual("AI gateway availability check failed.", result.reason)

    def test_http_provider_reports_unavailable_when_gateway_is_unreachable(self) -> None:
        provider = HttpAiGatewayAvailabilityProvider(
            base_url="http://127.0.0.1:1",
            health_path="/health",
            timeout_seconds=0.1,
            api_key=None,
        )

        result = provider.check_availability()

        self.assertEqual("unavailable", result.status)
        self.assertTrue(result.configured)
        self.assertEqual("AI gateway availability check failed.", result.reason)

    def test_http_provider_reports_unavailable_when_base_url_is_invalid(self) -> None:
        provider = HttpAiGatewayAvailabilityProvider(
            base_url="not a url",
            health_path="/health",
            timeout_seconds=0.1,
            api_key=None,
        )

        result = provider.check_availability()

        self.assertEqual("unavailable", result.status)
        self.assertTrue(result.configured)
        self.assertEqual("AI gateway availability check failed.", result.reason)


if __name__ == "__main__":
    unittest.main()
