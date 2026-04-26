import logging
from datetime import UTC, datetime

from app.business.novel_generate.nodes.outline.application.dto import CreateSeedCommand
from app.business.novel_generate.nodes.outline.domain.models import Seed
from app.business.novel_generate.nodes.outline.domain.repositories import (
    OutlineRepository,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

_REQUIRED_SEED_FIELDS = {
    "title": "小说暂定标题",
    "genre": "题材",
    "protagonist": "主角设定",
    "core_conflict": "核心冲突",
    "story_direction": "大致走向",
}


def validate_seed_complete(command: CreateSeedCommand) -> None:
    missing = [
        field_name
        for field_name in _REQUIRED_SEED_FIELDS
        if not getattr(command, field_name).strip()
    ]
    if missing:
        raise ValueError(f"缺少必填字段: {', '.join(missing)}")


class CreateSeedUseCase:
    def __init__(self, repository: OutlineRepository) -> None:
        self._repository = repository

    def execute(self, command: CreateSeedCommand) -> Seed:
        validate_seed_complete(command)
        now = datetime.now(UTC)
        seed = Seed(
            title=command.title.strip(),
            genre=command.genre.strip(),
            protagonist=command.protagonist.strip(),
            core_conflict=command.core_conflict.strip(),
            story_direction=command.story_direction.strip(),
            additional_notes=command.additional_notes.strip()
            if command.additional_notes
            else None,
            created_at=now,
            updated_at=now,
        )
        saved = self._repository.save_seed(seed)
        logger.info("outline_seed_created", extra={"seed_id": str(saved.id)})
        return saved
