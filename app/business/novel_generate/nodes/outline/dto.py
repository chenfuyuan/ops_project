"""大纲节点 HTTP 与业务入口使用的请求/响应 DTO。

命令对象承载用户输入，响应对象只用于 HTTP 协议输出映射。
"""

from uuid import UUID

from pydantic import BaseModel, Field


class CreateSeedCommand(BaseModel):
    """创建结构化创作种子的输入。"""

    title: str
    genre: str
    protagonist: str
    core_conflict: str
    story_direction: str
    additional_notes: str | None = None


class UpdateVolumeCommand(BaseModel):
    """编辑骨架卷内容的输入。"""

    volume_id: UUID
    title: str | None = None
    turning_point: str | None = None


class UpdateChapterCommand(BaseModel):
    """编辑章节摘要内容的输入。"""

    chapter_id: UUID
    title: str | None = None
    summary: str | None = None


class SeedResponse(BaseModel):
    """HTTP 层返回的种子内容。"""

    id: UUID
    title: str
    genre: str
    protagonist: str
    core_conflict: str
    story_direction: str
    additional_notes: str | None = None


class SkeletonVolumeResponse(BaseModel):
    """HTTP 层返回的骨架卷。"""

    id: UUID
    skeleton_id: UUID
    sequence: int
    title: str
    turning_point: str


class SkeletonResponse(BaseModel):
    """HTTP 层返回的骨架及其卷列表。"""

    id: UUID
    seed_id: UUID
    status: str
    volumes: list[SkeletonVolumeResponse] = Field(default_factory=list)


class ChapterSummaryResponse(BaseModel):
    """HTTP 层返回的章节摘要。"""

    id: UUID
    volume_id: UUID
    sequence: int
    title: str
    summary: str
    is_stale: bool


class OutlineResponse(BaseModel):
    """HTTP 层返回的完整大纲聚合视图。"""

    seed: SeedResponse
    skeleton: SkeletonResponse
    chapters_by_volume: dict[UUID, list[ChapterSummaryResponse]]
    status: str
