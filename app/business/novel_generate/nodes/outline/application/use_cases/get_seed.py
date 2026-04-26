from uuid import UUID

from app.business.novel_generate.nodes.outline.domain.models import Seed
from app.business.novel_generate.nodes.outline.domain.repositories import (
    OutlineRepository,
)


class GetSeedUseCase:
    def __init__(self, repository: OutlineRepository) -> None:
        self._repository = repository

    def execute(self, seed_id: UUID) -> Seed:
        seed = self._repository.get_seed(seed_id)
        if seed is None:
            raise ValueError("种子未找到")
        return seed
