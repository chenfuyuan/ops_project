from pathlib import Path
import os
import sys
import unittest

from fastapi.testclient import TestClient
from celery import Celery

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.bootstrap.settings import load_settings
from app.bootstrap.worker import create_worker_app
from app.interfaces.http.app import app as http_app
from app.shared.infra.cache import create_cache_endpoint
from app.shared.infra.database import create_engine_from_settings
from app.shared.infra.migrations import migration_paths
from app.shared.infra.storage import create_object_storage_endpoint


class RuntimeValidationTest(unittest.TestCase):
    def test_api_healthcheck_is_available(self) -> None:
        client = TestClient(http_app)
        response = client.get("/health")

        self.assertEqual(200, response.status_code)
        self.assertEqual({"status": "ok"}, response.json())

    def test_worker_app_loads_task_configuration(self) -> None:
        previous_broker = os.environ.get("PERSON_UP_CELERY_BROKER_URL")
        previous_backend = os.environ.get("PERSON_UP_CELERY_RESULT_BACKEND")
        os.environ["PERSON_UP_CELERY_BROKER_URL"] = "redis://localhost:6379/0"
        os.environ["PERSON_UP_CELERY_RESULT_BACKEND"] = "redis://localhost:6379/1"

        try:
            app = create_worker_app()
        finally:
            if previous_broker is None:
                os.environ.pop("PERSON_UP_CELERY_BROKER_URL", None)
            else:
                os.environ["PERSON_UP_CELERY_BROKER_URL"] = previous_broker
            if previous_backend is None:
                os.environ.pop("PERSON_UP_CELERY_RESULT_BACKEND", None)
            else:
                os.environ["PERSON_UP_CELERY_RESULT_BACKEND"] = previous_backend

        self.assertIsInstance(app, Celery)
        self.assertEqual("redis://localhost:6379/0", app.conf.broker_url)

    def test_infrastructure_bootstraps_without_business_models(self) -> None:
        previous_database = os.environ.get("PERSON_UP_DATABASE_URL")
        previous_redis = os.environ.get("PERSON_UP_REDIS_URL")
        previous_storage_endpoint = os.environ.get("PERSON_UP_OBJECT_STORAGE_ENDPOINT_URL")
        previous_storage_bucket = os.environ.get("PERSON_UP_OBJECT_STORAGE_BUCKET")
        os.environ["PERSON_UP_DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
        os.environ["PERSON_UP_REDIS_URL"] = "redis://localhost:6379/0"
        os.environ["PERSON_UP_OBJECT_STORAGE_ENDPOINT_URL"] = "http://localhost:9000"
        os.environ["PERSON_UP_OBJECT_STORAGE_BUCKET"] = "person-up"

        try:
            settings = load_settings()
            engine = create_engine_from_settings(settings)
            cache = create_cache_endpoint(settings)
            storage = create_object_storage_endpoint(settings)
            paths = migration_paths()
        finally:
            if previous_database is None:
                os.environ.pop("PERSON_UP_DATABASE_URL", None)
            else:
                os.environ["PERSON_UP_DATABASE_URL"] = previous_database
            if previous_redis is None:
                os.environ.pop("PERSON_UP_REDIS_URL", None)
            else:
                os.environ["PERSON_UP_REDIS_URL"] = previous_redis
            if previous_storage_endpoint is None:
                os.environ.pop("PERSON_UP_OBJECT_STORAGE_ENDPOINT_URL", None)
            else:
                os.environ["PERSON_UP_OBJECT_STORAGE_ENDPOINT_URL"] = previous_storage_endpoint
            if previous_storage_bucket is None:
                os.environ.pop("PERSON_UP_OBJECT_STORAGE_BUCKET", None)
            else:
                os.environ["PERSON_UP_OBJECT_STORAGE_BUCKET"] = previous_storage_bucket

        self.assertEqual("sqlite+pysqlite:///:memory:", engine.url.render_as_string(hide_password=False))
        self.assertEqual("redis://localhost:6379/0", cache.url)
        self.assertEqual("person-up", storage.bucket)
        self.assertTrue(paths.root_dir.is_dir())

    def test_governance_checks_run_without_sample_business_logic(self) -> None:
        architecture_test = ROOT / "tests" / "architecture" / "test_architecture_rules.py"
        self.assertTrue(architecture_test.exists())
        self.assertFalse((ROOT / "app" / "business" / "example.py").exists())


if __name__ == "__main__":
    unittest.main()
