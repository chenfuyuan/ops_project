import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.bootstrap.novel_generate import create_outline_service
from app.business.novel_generate.nodes.outline.infrastructure.ai.outline_ai_adapter import (
    OutlineAiAdapter,
)
from app.business.novel_generate.nodes.outline.facade import OutlineFacade
from app.business.novel_generate.nodes.outline.infrastructure.persistence.outline_repository import (
    OutlineRepositoryImpl,
)


class NovelGenerateBootstrapTest(unittest.TestCase):
    def test_create_outline_service_wires_repository_and_ai_adapter(self) -> None:
        engine = create_engine("sqlite+pysqlite:///:memory:")
        service = create_outline_service(object(), sessionmaker(bind=engine))

        self.assertIsInstance(service, OutlineFacade)
        self.assertIsInstance(service._repository, OutlineRepositoryImpl)
        self.assertIsInstance(service._generate_skeleton._ai_port, OutlineAiAdapter)


if __name__ == "__main__":
    unittest.main()
