"""大纲节点领域资源 repository 抽象。

该协议描述应用层对大纲持久化边界的需求，方法以 Seed、Skeleton、Volume、Chapter
和 Outline 等领域资源命名，不暴露 ORM session、SQLAlchemy record 或事务实现细节。
"""

from typing import Protocol
from uuid import UUID

from app.business.novel_generate.nodes.outline.domain.models import (
    ChapterSummary,
    Outline,
    Seed,
    Skeleton,
    SkeletonVolume,
)


class OutlineRepository(Protocol):
    """大纲节点的领域持久化端口。"""

    def save_seed(self, seed: Seed) -> Seed:
        """保存创作种子并返回持久化后的领域实体。"""
        ...

    def get_seed(self, seed_id: UUID) -> Seed | None:
        """按 ID 读取创作种子，未找到时返回 None。"""
        ...

    def save_skeleton(self, skeleton: Skeleton) -> Skeleton:
        """保存 seed 当前骨架；实现需维护同一 seed 单当前骨架约束。"""
        ...

    def get_skeleton(self, skeleton_id: UUID) -> Skeleton | None:
        """按 ID 读取骨架及其卷列表。"""
        ...

    def get_skeleton_by_seed(self, seed_id: UUID) -> Skeleton | None:
        """读取 seed 当前生效骨架。"""
        ...

    def get_volume(self, volume_id: UUID) -> SkeletonVolume | None:
        """按 ID 读取骨架卷。"""
        ...

    def get_chapter_summary(self, chapter_id: UUID) -> ChapterSummary | None:
        """按 ID 读取章节摘要。"""
        ...

    def save_chapter_summaries(
        self, summaries: list[ChapterSummary]
    ) -> list[ChapterSummary]:
        """保存某个卷的章节摘要列表，通常用于替换该卷旧展开结果。"""
        ...

    def get_chapters_by_volume(self, volume_id: UUID) -> list[ChapterSummary]:
        """按卷读取章节摘要列表，返回顺序应保持章节序号升序。"""
        ...

    def delete_chapters_by_volume(self, volume_id: UUID) -> None:
        """删除某个卷下的章节摘要。"""
        ...

    def mark_chapters_stale(self, volume_id: UUID) -> None:
        """将某个卷下的既有章节摘要标记为过期。"""
        ...

    def update_skeleton_volume(self, volume: SkeletonVolume) -> SkeletonVolume:
        """保存作者对骨架卷的编辑并返回更新后的领域实体。"""
        ...

    def update_chapter_summary(self, chapter: ChapterSummary) -> ChapterSummary:
        """保存作者对章节摘要的编辑并返回更新后的领域实体。"""
        ...

    def save_outline(self, outline: Outline) -> Outline:
        """保存 seed 维度大纲聚合视图。"""
        ...

    def get_outline_by_seed(self, seed_id: UUID) -> Outline | None:
        """读取 seed 维度大纲聚合视图。"""
        ...
