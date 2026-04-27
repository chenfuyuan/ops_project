"""确认大纲骨架用例。

确认动作是骨架从草稿进入可展开状态的唯一入口。该用例负责读取骨架、执行领域
状态校验、写入确认时间，并保存状态变化。
"""

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
    """将骨架草稿确认成可展开状态的应用服务。"""

    def __init__(self, repository: OutlineRepository) -> None:
        """注入大纲 repository 抽象。"""
        self._repository = repository

    def execute(self, skeleton_id: UUID) -> Skeleton:
        """确认指定骨架。

        只有草稿态骨架可以被确认；确认后记录 confirmed_at，后续卷展开依赖该状态作为
        前置条件。
        """
        logger.info(
            "outline_skeleton_confirmation_started",
            extra={"skeleton_id": str(skeleton_id)},
        )
        skeleton = self._repository.get_skeleton(skeleton_id)
        if skeleton is None:
            logger.warning(
                "outline_skeleton_not_found",
                extra={"skeleton_id": str(skeleton_id), "stage": "confirm_skeleton"},
            )
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
