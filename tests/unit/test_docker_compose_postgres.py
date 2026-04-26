from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
COMPOSE = ROOT / "docker-compose.yml"


class DockerComposePostgresTest(unittest.TestCase):
    def test_compose_defines_postgres_service_for_local_persistence(self) -> None:
        compose = COMPOSE.read_text()

        self.assertIn("postgres:", compose)
        self.assertIn("postgres:16-alpine", compose)
        self.assertIn("POSTGRES_DB: person_up", compose)
        self.assertIn("pg_isready -U person_up -d person_up", compose)

    def test_api_and_worker_receive_postgresql_database_url(self) -> None:
        compose = COMPOSE.read_text()
        database_url = (
            "postgresql+psycopg://person_up:person_up@postgres:5432/person_up"
        )

        self.assertGreaterEqual(compose.count(f"PERSON_UP_DATABASE_URL: {database_url}"), 2)
        self.assertIn("postgres:\n        condition: service_healthy", compose)


if __name__ == "__main__":
    unittest.main()
