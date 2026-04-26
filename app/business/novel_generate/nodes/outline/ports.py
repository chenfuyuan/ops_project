"""大纲节点对外部能力的业务端口定义。

端口使用大纲业务语言描述需要什么能力，由 infrastructure 和 bootstrap 选择具体实现。
"""

from typing import Protocol
from uuid import UUID

from app.business.novel_generate.nodes.outline.entities import (
    ChapterSummary,
    Outline,
    Seed,
    Skeleton,
    SkeletonVolume,
)


class OutlineRepository(Protocol):
    """大纲节点需要的持久化能力。"""

    def save_seed(self, seed: Seed) -> Seed:
        """保存创作种子并返回带稳定 ID 的 seed。"""

    def get_seed(self, seed_id: UUID) -> Seed | None:
        """按 ID 获取创作种子，未找到时返回 None。"""

    def save_skeleton(self, skeleton: Skeleton) -> Skeleton:
        """保存骨架；实现可替换同一 seed 下的旧骨架。"""

    def get_skeleton(self, skeleton_id: UUID) -> Skeleton | None:
        """按 ID 获取骨架及其卷列表，未找到时返回 None。"""

    def get_skeleton_by_seed(self, seed_id: UUID) -> Skeleton | None:
        """获取某个 seed 当前生效的骨架，未生成时返回 None。"""

    def get_volume(self, volume_id: UUID) -> SkeletonVolume | None:
        """按 ID 获取骨架卷，未找到时返回 None。"""

    def get_chapter_summary(self, chapter_id: UUID) -> ChapterSummary | None:
        """按 ID 获取章节摘要，未找到时返回 None。"""

    def save_chapter_summaries(
        self, summaries: list[ChapterSummary]
    ) -> list[ChapterSummary]:
        """保存某个卷的章节摘要；实现可替换同卷旧摘要。"""

    def get_chapters_by_volume(self, volume_id: UUID) -> list[ChapterSummary]:
        """按卷 ID 返回已保存章节摘要，结果应按章节顺序排列。"""

    def delete_chapters_by_volume(self, volume_id: UUID) -> None:
        """删除某个卷下的章节摘要，用于重新展开前清理。"""

    def mark_chapters_stale(self, volume_id: UUID) -> None:
        """将某个卷下的既有章节摘要标记为过期。"""

    def update_skeleton_volume(self, volume: SkeletonVolume) -> SkeletonVolume:
        """保存作者对骨架卷标题或转折点的编辑。"""

    def update_chapter_summary(self, chapter: ChapterSummary) -> ChapterSummary:
        """保存作者对单个章节标题或摘要的编辑。"""

    def save_outline(self, outline: Outline) -> Outline:
        """保存 seed 维度的完整大纲聚合状态。"""

    def get_outline_by_seed(self, seed_id: UUID) -> Outline | None:
        """按 seed ID 获取已保存的大纲聚合视图，未保存时返回 None。"""


class OutlineAiPort(Protocol):
    """大纲节点需要的 AI 生成能力。"""

    def generate_skeleton(self, seed: Seed) -> list[SkeletonVolume]:
        """基于创作种子生成粗粒度骨架卷。"""

    def expand_volume(
        self, seed: Seed, skeleton: Skeleton, volume: SkeletonVolume
    ) -> list[ChapterSummary]:
        """基于已确认骨架展开指定卷的章节摘要。"""
