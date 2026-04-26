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
    def __init__(self, repository: OutlineRepository) -> None:
        self._repository = repository

    def execute(self, command: UpdateChapterCommand) -> ChapterSummary:
        chapter = self._repository.get_chapter_summary(command.chapter_id)
        if chapter is None:
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
