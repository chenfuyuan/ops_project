from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import tempfile
from threading import Thread
import unittest

from fastapi.testclient import TestClient

from app.bootstrap.api import create_api_app


class RuntimeHealthHandler(BaseHTTPRequestHandler):
    authorization_header = None
    post_authorization_header = None
    posted_payload = None

    def do_GET(self) -> None:
        type(self).authorization_header = self.headers.get("Authorization")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def do_POST(self) -> None:
        if self.path != "/v1/chat/completions":
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length)
        type(self).post_authorization_header = self.headers.get("Authorization")
        type(self).posted_payload = json.loads(body.decode("utf-8"))

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps(
                {
                    "id": "chatcmpl-test",
                    "choices": [{"message": {"content": "pong"}}],
                    "usage": {"prompt_tokens": 1, "completion_tokens": 1},
                }
            ).encode("utf-8")
        )

    def log_message(self, format: str, *args: object) -> None:
        return None


class LocalRuntimeHealthServer:
    def __init__(self) -> None:
        RuntimeHealthHandler.authorization_header = None
        RuntimeHealthHandler.post_authorization_header = None
        RuntimeHealthHandler.posted_payload = None
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), RuntimeHealthHandler)
        self._thread = Thread(target=self._server.serve_forever, daemon=True)

    @property
    def base_url(self) -> str:
        host, port = self._server.server_address
        return f"http://{host}:{port}"

    @property
    def authorization_header(self) -> str | None:
        return RuntimeHealthHandler.authorization_header

    @property
    def post_authorization_header(self) -> str | None:
        return RuntimeHealthHandler.post_authorization_header

    @property
    def posted_payload(self) -> dict | None:
        return RuntimeHealthHandler.posted_payload

    def __enter__(self) -> "LocalRuntimeHealthServer":
        self._thread.start()
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=2)


class AiGatewayRuntimeWiringTest(unittest.TestCase):
    def test_create_api_app_reports_safe_503_when_config_path_points_to_missing_file(
        self,
    ) -> None:
        previous_config_path = os.environ.get("AI_GATEWAY_CONFIG_PATH")
        os.environ["AI_GATEWAY_CONFIG_PATH"] = (
            "/tmp/person-up-missing-ai-gateway-config.json"
        )

        try:
            client = TestClient(create_api_app())
            response = client.get("/ai-gateway/availability")
        finally:
            if previous_config_path is None:
                os.environ.pop("AI_GATEWAY_CONFIG_PATH", None)
            else:
                os.environ["AI_GATEWAY_CONFIG_PATH"] = previous_config_path

        self.assertEqual(503, response.status_code)
        self.assertEqual("unavailable", response.json()["status"])
        self.assertTrue(response.json()["configured"])
        self.assertEqual(
            "AI gateway config could not be loaded.", response.json()["reason"]
        )

    def test_create_api_app_reports_safe_503_when_config_path_points_to_directory(
        self,
    ) -> None:
        previous_config_path = os.environ.get("AI_GATEWAY_CONFIG_PATH")

        try:
            with tempfile.TemporaryDirectory() as directory:
                os.environ["AI_GATEWAY_CONFIG_PATH"] = directory

                client = TestClient(create_api_app())
                response = client.get("/ai-gateway/availability")
        finally:
            if previous_config_path is None:
                os.environ.pop("AI_GATEWAY_CONFIG_PATH", None)
            else:
                os.environ["AI_GATEWAY_CONFIG_PATH"] = previous_config_path

        self.assertEqual(503, response.status_code)
        self.assertEqual("unavailable", response.json()["status"])
        self.assertTrue(response.json()["configured"])
        self.assertEqual(
            "AI gateway config could not be loaded.", response.json()["reason"]
        )

    def test_create_api_app_reports_safe_503_when_api_key_env_is_missing(self) -> None:
        previous_values = {
            name: os.environ.get(name)
            for name in ("AI_GATEWAY_CONFIG_PATH", "AI_GATEWAY_API_KEY")
        }

        try:
            with tempfile.TemporaryDirectory() as directory:
                config_path = Path(directory) / "ai_gateway.json"
                config_path.write_text(
                    json.dumps(
                        {
                            "profiles": [
                                {
                                    "name": "smoke-test",
                                    "provider": "default",
                                    "model": "test-model",
                                    "capability_tags": [],
                                    "context_window": 8192,
                                    "cost_tier": "balanced",
                                    "timeout_seconds": 2,
                                    "retry_attempts": 0,
                                }
                            ],
                            "providers": [
                                {
                                    "name": "default",
                                    "kind": "openai-compatible",
                                    "base_url": "https://example.test/v1",
                                    "api_key_env": "AI_GATEWAY_API_KEY",
                                }
                            ],
                        }
                    ),
                    encoding="utf-8",
                )
                os.environ["AI_GATEWAY_CONFIG_PATH"] = str(config_path)
                os.environ.pop("AI_GATEWAY_API_KEY", None)

                client = TestClient(create_api_app())
                response = client.get("/ai-gateway/availability")
        finally:
            for name, value in previous_values.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value

        self.assertEqual(503, response.status_code)
        self.assertEqual("unavailable", response.json()["status"])
        self.assertTrue(response.json()["configured"])
        self.assertEqual(
            "AI gateway config could not be loaded.", response.json()["reason"]
        )

    def test_unconfigured_gateway_is_reported_through_bootstrapped_app(self) -> None:
        previous_config_path = os.environ.get("AI_GATEWAY_CONFIG_PATH")
        os.environ.pop("AI_GATEWAY_CONFIG_PATH", None)

        try:
            client = TestClient(create_api_app())
            response = client.get("/ai-gateway/availability")
        finally:
            if previous_config_path is not None:
                os.environ["AI_GATEWAY_CONFIG_PATH"] = previous_config_path

        self.assertEqual(503, response.status_code)
        self.assertEqual("unavailable", response.json()["status"])
        self.assertFalse(response.json()["configured"])
        self.assertEqual(
            "AI gateway config path is not configured.",
            response.json()["reason"],
        )

    def test_configured_gateway_is_checked_with_existing_gateway_config(self) -> None:
        previous_values = {
            name: os.environ.get(name)
            for name in ("AI_GATEWAY_CONFIG_PATH", "AI_GATEWAY_API_KEY")
        }

        try:
            with tempfile.TemporaryDirectory() as directory:
                with LocalRuntimeHealthServer() as server:
                    config_path = Path(directory) / "ai_gateway.json"
                    config_path.write_text(
                        json.dumps(
                            {
                                "profiles": [
                                    {
                                        "name": "smoke-test",
                                        "provider": "default",
                                        "model": "test-model",
                                        "capability_tags": [],
                                        "context_window": 8192,
                                        "cost_tier": "balanced",
                                        "timeout_seconds": 2,
                                        "retry_attempts": 0,
                                    }
                                ],
                                "providers": [
                                    {
                                        "name": "default",
                                        "kind": "openai-compatible",
                                        "base_url": server.base_url,
                                        "api_key_env": "AI_GATEWAY_API_KEY",
                                    }
                                ],
                            }
                        ),
                        encoding="utf-8",
                    )
                    os.environ["AI_GATEWAY_CONFIG_PATH"] = str(config_path)
                    os.environ["AI_GATEWAY_API_KEY"] = "shared-token"

                    client = TestClient(create_api_app())
                    response = client.get("/ai-gateway/availability")
        finally:
            for name, value in previous_values.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value

        self.assertEqual(200, response.status_code)
        self.assertEqual("available", response.json()["status"])
        self.assertTrue(response.json()["configured"])
        self.assertEqual("Bearer shared-token", server.authorization_header)

    def test_configured_gateway_generate_uses_existing_gateway_config(self) -> None:
        previous_values = {
            name: os.environ.get(name)
            for name in ("AI_GATEWAY_CONFIG_PATH", "AI_GATEWAY_API_KEY")
        }

        try:
            with tempfile.TemporaryDirectory() as directory:
                with LocalRuntimeHealthServer() as server:
                    config_path = Path(directory) / "ai_gateway.json"
                    config_path.write_text(
                        json.dumps(
                            {
                                "profiles": [
                                    {
                                        "name": "smoke-test",
                                        "provider": "default",
                                        "model": "test-model",
                                        "capability_tags": [],
                                        "context_window": 8192,
                                        "cost_tier": "balanced",
                                        "timeout_seconds": 2,
                                        "retry_attempts": 0,
                                    }
                                ],
                                "providers": [
                                    {
                                        "name": "default",
                                        "kind": "openai-compatible",
                                        "base_url": f"{server.base_url}/v1",
                                        "api_key_env": "AI_GATEWAY_API_KEY",
                                    }
                                ],
                            }
                        ),
                        encoding="utf-8",
                    )
                    os.environ["AI_GATEWAY_CONFIG_PATH"] = str(config_path)
                    os.environ["AI_GATEWAY_API_KEY"] = "shared-token"

                    client = TestClient(create_api_app())
                    response = client.post(
                        "/ai-gateway/generate",
                        json={
                            "capability_profile": "smoke-test",
                            "messages": [{"role": "user", "content": "ping"}],
                            "output_mode": "text",
                        },
                    )
        finally:
            for name, value in previous_values.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value

        self.assertEqual(200, response.status_code)
        self.assertEqual("pong", response.json()["content"])
        self.assertEqual("Bearer shared-token", server.post_authorization_header)
        self.assertEqual("test-model", server.posted_payload["model"])


if __name__ == "__main__":
    unittest.main()
