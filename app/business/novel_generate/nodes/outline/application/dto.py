"""大纲节点应用层 DTO。"""

from uuid import UUID

from pydantic import BaseModel, Field


class CreateSeedCommand(BaseModel):
    title: str
    genre: str
    protagonist: str
    core_conflict: str
    story_direction: str
    additional_notes: str | None = None


class UpdateVolumeCommand(BaseModel):
    volume_id: UUID
    title: str | None = None
    turning_point: str | None = None


class UpdateChapterCommand(BaseModel):
    chapter_id: UUID
    title: str | None = None
    summary: str | None = None


class SeedResponse(BaseModel):
    id: UUID
    title: str
    genre: str
    protagonist: str
    core_conflict: str
    story_direction: str
    additional_notes: str | None = None


class SkeletonVolumeResponse(BaseModel):
    id: UUID
    skeleton_id: UUID
    sequence: int
    title: str
    turning_point: str


class SkeletonResponse(BaseModel):
    id: UUID
    seed_id: UUID
    status: str
    volumes: list[SkeletonVolumeResponse] = Field(default_factory=list)


class ChapterSummaryResponse(BaseModel):
    id: UUID
    volume_id: UUID
    sequence: int
    title: str
    summary: str
    is_stale: bool


class OutlineResponse(BaseModel):
    seed: SeedResponse
    skeleton: SkeletonResponse
    chapters_by_volume: dict[UUID, list[ChapterSummaryResponse]]
    status: str
