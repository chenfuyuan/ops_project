"""构建 seed 维度大纲聚合视图用例。

该用例把 Seed、当前 Skeleton 与各卷章节摘要聚合成 Outline，并计算整体完成状态。
读取视图时会顺手保存聚合结果，使后续查询可以复用稳定的 outline 记录。
"""

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
    """读取并刷新大纲聚合视图的应用服务。"""

    def __init__(self, repository: OutlineRepository, get_seed: GetSeedUseCase) -> None:
        """注入 repository 与 seed 查询用例。"""
        self._repository = repository
        self._get_seed = get_seed

    def execute(self, seed_id: UUID) -> Outline:
        """构建 seed 当前大纲视图。

        COMPLETE 要求骨架已确认、存在卷，并且每个卷至少有一个章节摘要；否则大纲仍
        处于 IN_PROGRESS，方便前端或流程层继续引导用户补齐展开结果。
        """
        logger.info("outline_view_build_started", extra={"seed_id": str(seed_id)})
        seed = self._get_seed.execute(seed_id)
        skeleton = self._repository.get_skeleton_by_seed(seed.id)
        if skeleton is None:
            logger.warning(
                "outline_view_missing_skeleton", extra={"seed_id": str(seed.id)}
            )
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
                "outline_id": str(saved.id),
                "status": saved.status.value,
                "volume_count": len(skeleton.volumes),
                "chapter_count": sum(
                    len(chapters) for chapters in chapters_by_volume.values()
                ),
            },
        )
        return saved
