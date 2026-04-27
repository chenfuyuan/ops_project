"""更新骨架卷用例。

作者调整卷标题或转折点后，原有章节摘要可能不再匹配新的卷设定，因此本用例在保存
卷修改后将该卷章节摘要标记为过期，而不是直接删除作者仍可能参考的历史结果。
"""

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
    """保存骨架卷编辑并维护章节摘要过期状态。"""

    def __init__(self, repository: OutlineRepository) -> None:
        """注入大纲 repository 抽象。"""
        self._repository = repository

    def execute(self, command: UpdateVolumeCommand) -> SkeletonVolume:
        """更新骨架卷标题或转折点。

        None 表示字段不变；非 None 字符串会去除首尾空白。任何卷级设定变化都会让
        已生成章节摘要变为 stale，提示后续需要重新展开。
        """
        logger.info(
            "outline_volume_update_started", extra={"volume_id": str(command.volume_id)}
        )
        volume = self._repository.get_volume(command.volume_id)
        if volume is None:
            logger.warning(
                "outline_volume_not_found",
                extra={"volume_id": str(command.volume_id), "stage": "update_volume"},
            )
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
