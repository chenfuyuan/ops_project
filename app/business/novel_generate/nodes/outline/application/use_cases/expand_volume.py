import logging
from datetime import UTC, datetime
from uuid import UUID

from app.business.novel_generate.nodes.outline.application.ports import OutlineAiPort
from app.business.novel_generate.nodes.outline.application.use_cases.get_seed import (
    GetSeedUseCase,
)
from app.business.novel_generate.nodes.outline.domain.models import ChapterSummary
from app.business.novel_generate.nodes.outline.domain.repositories import (
    OutlineRepository,
)
from app.business.novel_generate.nodes.outline.domain.rules import (
    require_confirmed_skeleton,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ExpandVolumeUseCase:
    def __init__(
        self,
        repository: OutlineRepository,
        ai_port: OutlineAiPort,
        get_seed: GetSeedUseCase,
    ) -> None:
        self._repository = repository
        self._ai_port = ai_port
        self._get_seed = get_seed

    def execute(self, skeleton_id: UUID, volume_id: UUID) -> list[ChapterSummary]:
        skeleton = self._repository.get_skeleton(skeleton_id)
        if skeleton is None:
            raise ValueError("骨架未找到")
        require_confirmed_skeleton(skeleton)
        volume = next((item for item in skeleton.volumes if item.id == volume_id), None)
        if volume is None:
            raise ValueError("骨架卷未找到")
        seed = self._get_seed.execute(skeleton.seed_id)
        logger.info(
            "outline_volume_expansion_started",
            extra={"skeleton_id": str(skeleton.id), "volume_id": str(volume.id)},
        )
        summaries = self._ai_port.expand_volume(seed, skeleton, volume)
        now = datetime.now(UTC)
        for summary in summaries:
            summary.volume_id = volume.id
            summary.created_at = now
            summary.updated_at = now
            summary.is_stale = False
        saved = self._repository.save_chapter_summaries(summaries)
        logger.info(
            "outline_volume_expansion_completed",
            extra={
                "skeleton_id": str(skeleton.id),
                "volume_id": str(volume.id),
                "chapter_count": len(saved),
            },
        )
        return saved
