from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
HTTP_TESTS_DIR = ROOT / "tests" / "http"


class HttpRequestInterfacesTest(unittest.TestCase):
    def test_http_request_directory_documents_available_manual_requests(self) -> None:
        readme = HTTP_TESTS_DIR / "README.md"
        health_request = HTTP_TESTS_DIR / "health.http"
        ai_gateway_request = HTTP_TESTS_DIR / "ai_gateway.http"

        self.assertTrue(readme.is_file())
        self.assertTrue(health_request.is_file())
        self.assertTrue(ai_gateway_request.is_file())

        readme_text = readme.read_text()
        self.assertIn("uv run uvicorn app.api:app", readme_text)
        self.assertIn("AI_GATEWAY_CONFIG_PATH", readme_text)
        self.assertIn("config/ai_gateway.example.json", readme_text)
        self.assertIn("GET {{baseUrl}}/health", health_request.read_text())
        ai_gateway_request_text = ai_gateway_request.read_text()
        self.assertIn(
            "GET {{baseUrl}}/ai-gateway/availability",
            ai_gateway_request_text,
        )
        self.assertIn(
            "POST {{baseUrl}}/ai-gateway/generate",
            ai_gateway_request_text,
        )


if __name__ == "__main__":
    unittest.main()
