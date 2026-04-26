import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.bootstrap.novel_generate import create_outline_service
from app.business.novel_generate.nodes.outline.infrastructure.ai_adapter import OutlineAiAdapter
from app.business.novel_generate.nodes.outline.infrastructure.repository import OutlineRepositoryImpl
from app.business.novel_generate.nodes.outline.service import OutlineNodeService


class NovelGenerateBootstrapTest(unittest.TestCase):
    def test_create_outline_service_wires_repository_and_ai_adapter(self) -> None:
        engine = create_engine("sqlite+pysqlite:///:memory:")
        service = create_outline_service(object(), sessionmaker(bind=engine))

        self.assertIsInstance(service, OutlineNodeService)
        self.assertIsInstance(service._repository, OutlineRepositoryImpl)
        self.assertIsInstance(service._ai_port, OutlineAiAdapter)


if __name__ == "__main__":
    unittest.main()
