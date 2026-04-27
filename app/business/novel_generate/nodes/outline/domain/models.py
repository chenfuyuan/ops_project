"""大纲节点领域模型。

领域层只表达小说大纲生成的业务状态：创作种子、骨架、骨架卷、章节摘要与最终
聚合视图。这里不依赖 ORM、HTTP、AI gateway 或其他基础设施类型，保证 use case
可以围绕纯领域对象编排业务行为。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class SkeletonStatus(StrEnum):
    """骨架生命周期状态。"""

    DRAFT = "draft"
    CONFIRMED = "confirmed"


class OutlineStatus(StrEnum):
    """seed 维度大纲聚合完成度。"""

    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


def utc_now() -> datetime:
    """生成 timezone-aware UTC 时间，避免领域对象混用本地时区。"""
    return datetime.now(UTC)


@dataclass
class Seed:
    """作者输入的创作种子，是后续骨架生成和卷展开的根输入。"""

    title: str
    genre: str
    protagonist: str
    core_conflict: str
    story_direction: str
    additional_notes: str | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass
class SkeletonVolume:
    """骨架中的一个卷，记录卷顺序、标题和核心转折点。"""

    skeleton_id: UUID | None
    sequence: int
    title: str
    turning_point: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass
class Skeleton:
    """围绕单个 Seed 生成的卷级故事骨架。"""

    seed_id: UUID
    volumes: list[SkeletonVolume]
    status: SkeletonStatus = SkeletonStatus.DRAFT
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
    confirmed_at: datetime | None = None


@dataclass
class ChapterSummary:
    """某个骨架卷下的章节级摘要。"""

    volume_id: UUID
    sequence: int
    title: str
    summary: str
    is_stale: bool = False
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass
class Outline:
    """seed 维度的大纲聚合视图。

    chapters_by_volume 使用 volume_id 分组，便于读取时保持骨架卷与章节摘要的对应
    关系；status 由骨架状态和各卷章节是否齐全共同决定。
    """

    seed: Seed
    skeleton: Skeleton
    chapters_by_volume: dict[UUID, list[ChapterSummary]]
    status: OutlineStatus
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    @property
    def seed_id(self) -> UUID:
        """返回聚合根 seed 的 ID，供 repository 按 seed 维度保存视图。"""
        return self.seed.id

    @property
    def skeleton_id(self) -> UUID:
        """返回当前聚合视图关联的骨架 ID。"""
        return self.skeleton.id
