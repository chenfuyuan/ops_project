import logging
from uuid import UUID, uuid4

from app.business.novel_generate.nodes.outline.application.use_cases.get_seed import (
    GetSeedUseCase,
)
from app.business.novel_generate.nodes.outline.domain.models import (
    Outline,
    OutlineStatus,
    SkeletonStatus,
)
from app.business.novel_generate.nodes.outline.domain.repositories import (
    OutlineRepository,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class GetOutlineUseCase:
    def __init__(self, repository: OutlineRepository, get_seed: GetSeedUseCase) -> None:
        self._repository = repository
        self._get_seed = get_seed

    def execute(self, seed_id: UUID) -> Outline:
        seed = self._get_seed.execute(seed_id)
        skeleton = self._repository.get_skeleton_by_seed(seed.id)
        if skeleton is None:
            raise ValueError("大纲未找到")
        chapters_by_volume = {
            volume.id: self._repository.get_chapters_by_volume(volume.id)
            for volume in skeleton.volumes
        }
        is_complete = (
            skeleton.status is SkeletonStatus.CONFIRMED
            and bool(skeleton.volumes)
            and all(chapters_by_volume[volume.id] for volume in skeleton.volumes)
        )
        existing = self._repository.get_outline_by_seed(seed.id)
        outline = Outline(
            id=existing.id if existing is not None else uuid4(),
            seed=seed,
            skeleton=skeleton,
            chapters_by_volume=chapters_by_volume,
            status=OutlineStatus.COMPLETE if is_complete else OutlineStatus.IN_PROGRESS,
        )
        saved = self._repository.save_outline(outline)
        logger.info(
            "outline_view_built",
            extra={
                "seed_id": str(seed.id),
                "skeleton_id": str(skeleton.id),
                "status": saved.status.value,
                "volume_count": len(skeleton.volumes),
                "chapter_count": sum(
                    len(chapters) for chapters in chapters_by_volume.values()
                ),
            },
        )
        return saved
