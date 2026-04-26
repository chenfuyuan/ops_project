"""大纲节点领域模型。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class SkeletonStatus(StrEnum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"


class OutlineStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass
class Seed:
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
    skeleton_id: UUID | None
    sequence: int
    title: str
    turning_point: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass
class Skeleton:
    seed_id: UUID
    volumes: list[SkeletonVolume]
    status: SkeletonStatus = SkeletonStatus.DRAFT
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
    confirmed_at: datetime | None = None


@dataclass
class ChapterSummary:
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
    seed: Seed
    skeleton: Skeleton
    chapters_by_volume: dict[UUID, list[ChapterSummary]]
    status: OutlineStatus
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    @property
    def seed_id(self) -> UUID:
        return self.seed.id

    @property
    def skeleton_id(self) -> UUID:
        return self.skeleton.id
