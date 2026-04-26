import os
import unittest

from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from app.bootstrap.settings import load_settings
from app.shared.infra.database import (
    create_engine_from_settings,
    create_session_factory,
)


class DatabaseBootstrapTest(unittest.TestCase):
    def test_load_settings_reads_database_url(self) -> None:
        previous = os.environ.get("PERSON_UP_DATABASE_URL")
        os.environ["PERSON_UP_DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

        try:
            settings = load_settings()
        finally:
            if previous is None:
                os.environ.pop("PERSON_UP_DATABASE_URL", None)
            else:
                os.environ["PERSON_UP_DATABASE_URL"] = previous

        self.assertEqual("sqlite+pysqlite:///:memory:", settings.database_url)

    def test_load_settings_reads_postgresql_database_url(self) -> None:
        previous = os.environ.get("PERSON_UP_DATABASE_URL")
        os.environ["PERSON_UP_DATABASE_URL"] = (
            "postgresql+psycopg://person_up:person_up@localhost:5432/person_up"
        )

        try:
            settings = load_settings()
            engine = create_engine_from_settings(settings)
        finally:
            if previous is None:
                os.environ.pop("PERSON_UP_DATABASE_URL", None)
            else:
                os.environ["PERSON_UP_DATABASE_URL"] = previous

        self.assertEqual(
            "postgresql+psycopg://person_up:***@localhost:5432/person_up",
            engine.url.render_as_string(hide_password=True),
        )

    def test_create_engine_from_settings_uses_database_url(self) -> None:
        previous = os.environ.get("PERSON_UP_DATABASE_URL")
        os.environ["PERSON_UP_DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

        try:
            settings = load_settings()
            engine = create_engine_from_settings(settings)
        finally:
            if previous is None:
                os.environ.pop("PERSON_UP_DATABASE_URL", None)
            else:
                os.environ["PERSON_UP_DATABASE_URL"] = previous

        self.assertIsInstance(engine, Engine)
        self.assertEqual(
            "sqlite+pysqlite:///:memory:",
            engine.url.render_as_string(hide_password=True),
        )

    def test_create_session_factory_returns_sessionmaker(self) -> None:
        previous = os.environ.get("PERSON_UP_DATABASE_URL")
        os.environ["PERSON_UP_DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

        try:
            settings = load_settings()
            engine = create_engine_from_settings(settings)
            factory = create_session_factory(engine)
        finally:
            if previous is None:
                os.environ.pop("PERSON_UP_DATABASE_URL", None)
            else:
                os.environ["PERSON_UP_DATABASE_URL"] = previous

        self.assertIsInstance(factory, sessionmaker)
        self.assertIs(factory.kw["bind"], engine)


if __name__ == "__main__":
    unittest.main()
