import unittest

from app.bootstrap.api import create_api_app
from app.interfaces.http.app import app


class ApiBootstrapTest(unittest.TestCase):
    def test_create_api_app_returns_fastapi_instance(self) -> None:
        created_app = create_api_app()

        self.assertIs(app, created_app)
        self.assertEqual("Person Up Ops Project", created_app.title)


if __name__ == "__main__":
    unittest.main()
