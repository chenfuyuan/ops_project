from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class MigrationsConfigTest(unittest.TestCase):
    def test_alembic_root_config_exists_for_cli_execution(self) -> None:
        config = ROOT / "alembic.ini"

        self.assertTrue(config.exists())
        self.assertIn("script_location = alembic", config.read_text())

    def test_alembic_env_uses_runtime_database_url(self) -> None:
        env = ROOT / "alembic" / "env.py"
        content = env.read_text()

        self.assertIn("PERSON_UP_DATABASE_URL", content)
        self.assertIn("config.set_main_option", content)

    def test_dockerfile_copies_alembic_config(self) -> None:
        dockerfile = ROOT / "Dockerfile"

        self.assertIn("COPY alembic.ini", dockerfile.read_text())

if __name__ == "__main__":
    unittest.main()
