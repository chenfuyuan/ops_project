"""读取大纲创作种子用例。"""

import logging
from uuid import UUID

from app.business.novel_generate.nodes.outline.domain.models import Seed
from app.business.novel_generate.nodes.outline.domain.repositories import (
    OutlineRepository,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class GetSeedUseCase:
    """按 ID 读取 Seed 的应用服务。"""

    def __init__(self, repository: OutlineRepository) -> None:
        """注入 repository 抽象，避免读取流程绑定具体存储实现。"""
        self._repository = repository

    def execute(self, seed_id: UUID) -> Seed:
        """读取创作种子，未找到时抛出业务错误。"""
        seed = self._repository.get_seed(seed_id)
        if seed is None:
            logger.warning("outline_seed_not_found", extra={"seed_id": str(seed_id)})
            raise ValueError("种子未找到")
        logger.debug("outline_seed_loaded", extra={"seed_id": str(seed.id)})
        return seed
