import logging
from datetime import UTC, datetime
from uuid import UUID

from app.business.novel_generate.nodes.outline.domain.models import (
    Skeleton,
    SkeletonStatus,
)
from app.business.novel_generate.nodes.outline.domain.repositories import (
    OutlineRepository,
)
from app.business.novel_generate.nodes.outline.domain.rules import (
    require_draft_skeleton,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ConfirmSkeletonUseCase:
    def __init__(self, repository: OutlineRepository) -> None:
        self._repository = repository

    def execute(self, skeleton_id: UUID) -> Skeleton:
        skeleton = self._repository.get_skeleton(skeleton_id)
        if skeleton is None:
            raise ValueError("骨架未找到")
        require_draft_skeleton(skeleton)
        now = datetime.now(UTC)
        skeleton.status = SkeletonStatus.CONFIRMED
        skeleton.confirmed_at = now
        skeleton.updated_at = now
        saved = self._repository.save_skeleton(skeleton)
        logger.info(
            "outline_skeleton_confirmed",
            extra={"skeleton_id": str(saved.id), "seed_id": str(saved.seed_id)},
        )
        return saved
