"""展开大纲骨架卷用例。

该用例要求骨架已确认，然后调用 AI port 生成目标卷的章节摘要。为避免旧展开结果
继续参与聚合，repository 保存摘要时会按 volume 替换旧数据。
"""

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
    """将已确认骨架中的单个卷展开为章节摘要。"""

    def __init__(
        self,
        repository: OutlineRepository,
        ai_port: OutlineAiPort,
        get_seed: GetSeedUseCase,
    ) -> None:
        """注入 repository、AI port 与 seed 查询用例。"""
        self._repository = repository
        self._ai_port = ai_port
        self._get_seed = get_seed

    def execute(self, skeleton_id: UUID, volume_id: UUID) -> list[ChapterSummary]:
        """展开目标卷并返回保存后的章节摘要列表。

        volume 必须来自当前 skeleton.volumes，防止调用方用不相关的 volume_id 组合出
        跨骨架展开请求。
        """
        logger.info(
            "outline_volume_expansion_requested",
            extra={"skeleton_id": str(skeleton_id), "volume_id": str(volume_id)},
        )
        skeleton = self._repository.get_skeleton(skeleton_id)
        if skeleton is None:
            logger.warning(
                "outline_skeleton_not_found",
                extra={"skeleton_id": str(skeleton_id), "stage": "expand_volume"},
            )
            raise ValueError("骨架未找到")
        require_confirmed_skeleton(skeleton)
        volume = next((item for item in skeleton.volumes if item.id == volume_id), None)
        if volume is None:
            logger.warning(
                "outline_volume_not_found_in_skeleton",
                extra={"skeleton_id": str(skeleton.id), "volume_id": str(volume_id)},
            )
            raise ValueError("骨架卷未找到")
        seed = self._get_seed.execute(skeleton.seed_id)
        logger.info(
            "outline_volume_expansion_started",
            extra={"skeleton_id": str(skeleton.id), "volume_id": str(volume.id)},
        )
        summaries = self._ai_port.expand_volume(seed, skeleton, volume)
        logger.debug(
            "outline_volume_expansion_ai_result_received",
            extra={
                "skeleton_id": str(skeleton.id),
                "volume_id": str(volume.id),
                "chapter_count": len(summaries),
            },
        )
        now = datetime.now(UTC)
        for summary in summaries:
            # 章节归属、时间戳和过期标记由业务侧统一设置，避免信任 AI 输出这些状态字段。
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
