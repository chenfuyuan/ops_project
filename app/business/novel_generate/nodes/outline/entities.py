"""大纲节点领域实体和值对象。

实体只表达业务状态和聚合关系，不包含持久化、HTTP 或 AI provider 细节。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class SkeletonStatus(StrEnum):
    """骨架确认状态。"""

    DRAFT = "draft"
    CONFIRMED = "confirmed"


class OutlineStatus(StrEnum):
    """完整大纲展开状态。"""

    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


def utc_now() -> datetime:
    """返回 timezone-aware UTC 时间，避免实体默认时间使用本地时区。"""
    return datetime.now(UTC)


@dataclass
class Seed:
    """作者提交的结构化创作种子。"""

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
    """骨架中的粗粒度卷/幕。"""

    skeleton_id: UUID | None
    sequence: int
    title: str
    turning_point: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass
class Skeleton:
    """由种子生成并可由作者确认的粗粒度结构。"""

    seed_id: UUID
    volumes: list[SkeletonVolume]
    status: SkeletonStatus = SkeletonStatus.DRAFT
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
    confirmed_at: datetime | None = None


@dataclass
class ChapterSummary:
    """某个骨架卷下的章节摘要。"""

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
    """按种子聚合的完整大纲视图。"""

    seed: Seed
    skeleton: Skeleton
    chapters_by_volume: dict[UUID, list[ChapterSummary]]
    status: OutlineStatus
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    @property
    def seed_id(self) -> UUID:
        """返回聚合所属 seed 的稳定 ID，便于 repository 保存外键。"""
        return self.seed.id

    @property
    def skeleton_id(self) -> UUID:
        """返回聚合所属 skeleton 的稳定 ID，便于 repository 保存外键。"""
        return self.skeleton.id
