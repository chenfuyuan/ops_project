"""创建大纲创作种子用例。

该用例负责校验作者输入的最小必填信息、规范化前后空白，并把可持久化的 Seed
领域对象交给 repository。日志只记录 seed_id 和字段级摘要，不记录完整创作内容。
"""

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
    """校验创作种子必填字段是否提供有效文本。

    这里只检查应用层必须具备的最小输入，不判断题材、人物或剧情内容质量；失败日志
    只记录缺失字段名，避免泄露作者输入的正文。
    """
    missing = [
        field_name
        for field_name in _REQUIRED_SEED_FIELDS
        if not getattr(command, field_name).strip()
    ]
    if missing:
        logger.warning(
            "outline_seed_validation_failed",
            extra={"missing_fields": missing},
        )
        raise ValueError(f"缺少必填字段: {', '.join(missing)}")


class CreateSeedUseCase:
    """创建并保存大纲创作种子的应用服务。"""

    def __init__(self, repository: OutlineRepository) -> None:
        """注入大纲 repository 抽象，保持用例不依赖具体持久化实现。"""
        self._repository = repository

    def execute(self, command: CreateSeedCommand) -> Seed:
        """执行种子创建流程并返回持久化后的 Seed。

        command 字段会被去除首尾空白；additional_notes 为空时统一落为 None，避免
        持久化层同时出现空字符串和空值两种“无补充说明”表达。
        """
        logger.info("outline_seed_creation_started")
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
