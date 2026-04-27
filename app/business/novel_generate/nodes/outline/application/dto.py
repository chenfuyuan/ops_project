"""大纲节点应用层 DTO。

这些对象定义 facade / interface 与应用层之间的稳定数据边界。Command 表达一次
写操作的业务意图，Response 表达可安全返回给协议层的读取结果；领域实体与 ORM
record 不应直接穿透到外部协议边界。
"""

from uuid import UUID

from pydantic import BaseModel, Field


class CreateSeedCommand(BaseModel):
    """创建创作种子的命令。

    所有字符串字段都来自作者输入，校验和去空白在用例层完成；日志不得记录这些
    字段的完整内容。
    """

    title: str
    genre: str
    protagonist: str
    core_conflict: str
    story_direction: str
    additional_notes: str | None = None


class UpdateVolumeCommand(BaseModel):
    """更新骨架卷的命令；None 表示保持对应字段不变。"""

    volume_id: UUID
    title: str | None = None
    turning_point: str | None = None


class UpdateChapterCommand(BaseModel):
    """更新章节摘要的命令；None 表示保持对应字段不变。"""

    chapter_id: UUID
    title: str | None = None
    summary: str | None = None


class SeedResponse(BaseModel):
    """创作种子的协议层响应模型。"""

    id: UUID
    title: str
    genre: str
    protagonist: str
    core_conflict: str
    story_direction: str
    additional_notes: str | None = None


class SkeletonVolumeResponse(BaseModel):
    """骨架卷的协议层响应模型。"""

    id: UUID
    skeleton_id: UUID
    sequence: int
    title: str
    turning_point: str


class SkeletonResponse(BaseModel):
    """骨架聚合的协议层响应模型。"""

    id: UUID
    seed_id: UUID
    status: str
    volumes: list[SkeletonVolumeResponse] = Field(default_factory=list)


class ChapterSummaryResponse(BaseModel):
    """章节摘要的协议层响应模型。"""

    id: UUID
    volume_id: UUID
    sequence: int
    title: str
    summary: str
    is_stale: bool


class OutlineResponse(BaseModel):
    """seed 维度完整大纲视图的协议层响应模型。"""

    seed: SeedResponse
    skeleton: SkeletonResponse
    chapters_by_volume: dict[UUID, list[ChapterSummaryResponse]]
    status: str
