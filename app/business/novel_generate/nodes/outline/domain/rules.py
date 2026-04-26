"""大纲节点领域规则。"""

from app.business.novel_generate.nodes.outline.domain.models import (
    Skeleton,
    SkeletonStatus,
)


def require_draft_skeleton(skeleton: Skeleton) -> None:
    if skeleton.status is not SkeletonStatus.DRAFT:
        raise ValueError("骨架已确认，不可重复确认")


def require_confirmed_skeleton(skeleton: Skeleton) -> None:
    if skeleton.status is not SkeletonStatus.CONFIRMED:
        raise ValueError("骨架未确认，不可展开")
