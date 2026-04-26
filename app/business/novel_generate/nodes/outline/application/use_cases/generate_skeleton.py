import logging
from datetime import UTC, datetime
from uuid import UUID

from app.business.novel_generate.nodes.outline.application.ports import OutlineAiPort
from app.business.novel_generate.nodes.outline.application.use_cases.get_seed import (
    GetSeedUseCase,
)
from app.business.novel_generate.nodes.outline.domain.models import Skeleton
from app.business.novel_generate.nodes.outline.domain.repositories import (
    OutlineRepository,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class GenerateSkeletonUseCase:
    def __init__(
        self,
        repository: OutlineRepository,
        ai_port: OutlineAiPort,
        get_seed: GetSeedUseCase,
    ) -> None:
        self._repository = repository
        self._ai_port = ai_port
        self._get_seed = get_seed

    def execute(self, seed_id: UUID) -> Skeleton:
        seed = self._get_seed.execute(seed_id)
        logger.info(
            "outline_skeleton_generation_started", extra={"seed_id": str(seed.id)}
        )
        volumes = self._ai_port.generate_skeleton(seed)
        now = datetime.now(UTC)
        skeleton = Skeleton(
            seed_id=seed.id, volumes=volumes, created_at=now, updated_at=now
        )
        for volume in skeleton.volumes:
            volume.skeleton_id = skeleton.id
            volume.created_at = now
            volume.updated_at = now
        saved = self._repository.save_skeleton(skeleton)
        logger.info(
            "outline_skeleton_generation_completed",
            extra={
                "seed_id": str(saved.seed_id),
                "skeleton_id": str(saved.id),
                "volume_count": len(saved.volumes),
            },
        )
        return saved
