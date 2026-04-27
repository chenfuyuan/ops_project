"""大纲节点领域规则。

这里集中放置与骨架状态流转相关的不变量，避免状态判断散落在 use case 或
infrastructure 中。规则函数只依赖领域模型，抛出的 ValueError 由上层边界转换为
适合协议层的错误响应。
"""

from app.business.novel_generate.nodes.outline.domain.models import (
    Skeleton,
    SkeletonStatus,
)


def require_draft_skeleton(skeleton: Skeleton) -> None:
    """要求骨架仍处于草稿态。

    重复确认会破坏“确认时间”与后续展开前置条件的含义，因此非草稿态直接拒绝。
    """
    if skeleton.status is not SkeletonStatus.DRAFT:
        raise ValueError("骨架已确认，不可重复确认")


def require_confirmed_skeleton(skeleton: Skeleton) -> None:
    """要求骨架已确认后才能展开章节。"""
    if skeleton.status is not SkeletonStatus.CONFIRMED:
        raise ValueError("骨架未确认，不可展开")
