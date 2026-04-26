import os
import unittest

from fastapi.testclient import TestClient

from app.bootstrap.api import create_api_app


class ApiBootstrapTest(unittest.TestCase):
    def test_create_api_app_returns_runtime_wired_fastapi_instance(self) -> None:
        previous_config_path = os.environ.get("AI_GATEWAY_CONFIG_PATH")
        previous_database_url = os.environ.get("PERSON_UP_DATABASE_URL")
        os.environ.pop("AI_GATEWAY_CONFIG_PATH", None)
        os.environ.pop("PERSON_UP_DATABASE_URL", None)

        try:
            created_app = create_api_app()
            client = TestClient(created_app)
        finally:
            if previous_config_path is not None:
                os.environ["AI_GATEWAY_CONFIG_PATH"] = previous_config_path
            if previous_database_url is not None:
                os.environ["PERSON_UP_DATABASE_URL"] = previous_database_url

        self.assertEqual("Person Up Ops Project", created_app.title)
        self.assertEqual(200, client.get("/health").status_code)
        self.assertEqual(503, client.get("/ai-gateway/availability").status_code)
        response = client.post(
            "/api/outlines/seeds",
            json={
                "title": "群星回声",
                "genre": "科幻",
                "protagonist": "失忆领航员",
                "core_conflict": "殖民舰队争夺唯一航道",
                "story_direction": "主角发现真相",
            },
        )
        self.assertEqual(503, response.status_code)
        self.assertEqual({"detail": "outline service is not configured."}, response.json())


if __name__ == "__main__":
    unittest.main()
