"""更新章节摘要用例。"""

import logging
from datetime import UTC, datetime

from app.business.novel_generate.nodes.outline.application.dto import (
    UpdateChapterCommand,
)
from app.business.novel_generate.nodes.outline.domain.models import ChapterSummary
from app.business.novel_generate.nodes.outline.domain.repositories import (
    OutlineRepository,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class UpdateChapterUseCase:
    """保存作者对单个章节摘要的编辑。"""

    def __init__(self, repository: OutlineRepository) -> None:
        """注入大纲 repository 抽象。"""
        self._repository = repository

    def execute(self, command: UpdateChapterCommand) -> ChapterSummary:
        """更新章节标题或摘要正文。

        None 表示字段不变；非 None 字符串会去除首尾空白。日志只记录 chapter_id 和
        volume_id，不记录摘要正文。
        """
        logger.info(
            "outline_chapter_update_started",
            extra={"chapter_id": str(command.chapter_id)},
        )
        chapter = self._repository.get_chapter_summary(command.chapter_id)
        if chapter is None:
            logger.warning(
                "outline_chapter_not_found",
                extra={
                    "chapter_id": str(command.chapter_id),
                    "stage": "update_chapter",
                },
            )
            raise ValueError("章节摘要未找到")
        if command.title is not None:
            chapter.title = command.title.strip()
        if command.summary is not None:
            chapter.summary = command.summary.strip()
        chapter.updated_at = datetime.now(UTC)
        updated = self._repository.update_chapter_summary(chapter)
        logger.info(
            "outline_chapter_updated",
            extra={"chapter_id": str(updated.id), "volume_id": str(updated.volume_id)},
        )
        return updated
