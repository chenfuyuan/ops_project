import os
import unittest

from fastapi.testclient import TestClient

from app.bootstrap.api import create_api_app


class ApiBootstrapTest(unittest.TestCase):
    def test_create_api_app_returns_runtime_wired_fastapi_instance(self) -> None:
        previous_config_path = os.environ.get("AI_GATEWAY_CONFIG_PATH")
        os.environ.pop("AI_GATEWAY_CONFIG_PATH", None)

        try:
            created_app = create_api_app()
            client = TestClient(created_app)
        finally:
            if previous_config_path is not None:
                os.environ["AI_GATEWAY_CONFIG_PATH"] = previous_config_path

        self.assertEqual("Person Up Ops Project", created_app.title)
        self.assertEqual(200, client.get("/health").status_code)
        self.assertEqual(503, client.get("/ai-gateway/availability").status_code)


if __name__ == "__main__":
    unittest.main()
