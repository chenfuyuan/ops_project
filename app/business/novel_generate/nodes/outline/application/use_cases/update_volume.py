import logging
from datetime import UTC, datetime

from app.business.novel_generate.nodes.outline.application.dto import (
    UpdateVolumeCommand,
)
from app.business.novel_generate.nodes.outline.domain.models import SkeletonVolume
from app.business.novel_generate.nodes.outline.domain.repositories import (
    OutlineRepository,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class UpdateVolumeUseCase:
    def __init__(self, repository: OutlineRepository) -> None:
        self._repository = repository

    def execute(self, command: UpdateVolumeCommand) -> SkeletonVolume:
        volume = self._repository.get_volume(command.volume_id)
        if volume is None:
            raise ValueError("骨架卷未找到")
        if command.title is not None:
            volume.title = command.title.strip()
        if command.turning_point is not None:
            volume.turning_point = command.turning_point.strip()
        volume.updated_at = datetime.now(UTC)
        updated = self._repository.update_skeleton_volume(volume)
        self._repository.mark_chapters_stale(updated.id)
        logger.info(
            "outline_volume_updated",
            extra={
                "volume_id": str(updated.id),
                "skeleton_id": str(updated.skeleton_id)
                if updated.skeleton_id
                else None,
            },
        )
        return updated
