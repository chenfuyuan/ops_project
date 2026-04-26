"""大纲节点业务规则校验。

规则函数抛出稳定 ValueError 文案，供 service 和 HTTP 边界转换为用户可理解错误。
"""

from app.business.novel_generate.nodes.outline.dto import CreateSeedCommand
from app.business.novel_generate.nodes.outline.entities import Skeleton, SkeletonStatus

_REQUIRED_SEED_FIELDS = {
    "title": "小说暂定标题",
    "genre": "题材",
    "protagonist": "主角设定",
    "core_conflict": "核心冲突",
    "story_direction": "大致走向",
}


def validate_seed_complete(command: CreateSeedCommand) -> None:
    """校验种子必填字段，缺失时返回稳定字段名便于 HTTP 层透传。"""
    missing = [
        field_name
        for field_name in _REQUIRED_SEED_FIELDS
        if not getattr(command, field_name).strip()
    ]
    if missing:
        raise ValueError(f"缺少必填字段: {', '.join(missing)}")


def require_draft_skeleton(skeleton: Skeleton) -> None:
    """确认骨架前必须仍处于草稿状态。"""
    if skeleton.status is not SkeletonStatus.DRAFT:
        raise ValueError("骨架已确认，不可重复确认")


def require_confirmed_skeleton(skeleton: Skeleton) -> None:
    """展开章节前必须先完成骨架确认。"""
    if skeleton.status is not SkeletonStatus.CONFIRMED:
        raise ValueError("骨架未确认，不可展开")
