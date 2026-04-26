"""大纲节点业务编排服务。

本模块只处理创作种子、骨架、章节摘要和完整大纲的业务顺序，
具体 AI provider、HTTP 协议和 ORM 细节都通过 port 隔离在外部。
"""

import logging
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.business.novel_generate.nodes.outline.dto import (
    CreateSeedCommand,
    UpdateChapterCommand,
    UpdateVolumeCommand,
)
from app.business.novel_generate.nodes.outline.entities import (
    ChapterSummary,
    Outline,
    OutlineStatus,
    Seed,
    Skeleton,
    SkeletonStatus,
)
from app.business.novel_generate.nodes.outline.ports import (
    OutlineAiPort,
    OutlineRepository,
)
from app.business.novel_generate.nodes.outline.rules import (
    require_confirmed_skeleton,
    require_draft_skeleton,
    validate_seed_complete,
)


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class OutlineNodeService:
    """编排大纲节点用例，并保持业务核心只依赖 repository 与 AI port。"""

    def __init__(self, repository: OutlineRepository, ai_port: OutlineAiPort) -> None:
        self._repository = repository
        self._ai_port = ai_port

    def create_seed(self, command: CreateSeedCommand) -> Seed:
        """校验并持久化作者提交的结构化种子，返回可继续生成骨架的 seed。"""
        validate_seed_complete(command)
        now = datetime.now(UTC)
        seed = Seed(
            title=command.title.strip(),
            genre=command.genre.strip(),
            protagonist=command.protagonist.strip(),
            core_conflict=command.core_conflict.strip(),
            story_direction=command.story_direction.strip(),
            additional_notes=command.additional_notes.strip()
            if command.additional_notes
            else None,
            created_at=now,
            updated_at=now,
        )
        saved = self._repository.save_seed(seed)
        logger.info("outline_seed_created", extra={"seed_id": str(saved.id)})
        return saved

    def get_seed(self, seed_id: UUID) -> Seed:
        """按 ID 获取种子，未找到时抛出业务错误。"""
        seed = self._repository.get_seed(seed_id)
        if seed is None:
            raise ValueError("种子未找到")
        return seed

    def get_skeleton(self, skeleton_id: UUID) -> Skeleton:
        """按 ID 获取骨架及其卷列表。"""
        return self._get_skeleton(skeleton_id)

    def generate_skeleton(self, seed_id: UUID) -> Skeleton:
        """调用 AI port 生成骨架，并用新骨架替换同一种子的旧骨架。"""
        seed = self.get_seed(seed_id)
        logger.info("outline_skeleton_generation_started", extra={"seed_id": str(seed.id)})
        volumes = self._ai_port.generate_skeleton(seed)
        now = datetime.now(UTC)
        skeleton = Skeleton(seed_id=seed.id, volumes=volumes, created_at=now, updated_at=now)
        for volume in skeleton.volumes:
            volume.skeleton_id = skeleton.id
            volume.created_at = now
            volume.updated_at = now
        # 保存新骨架时 repository 会清理同一 seed 下的旧骨架和已展开章节。
        saved = self._repository.save_skeleton(skeleton)
        logger.info(
            "outline_skeleton_generation_completed",
            extra={
                "seed_id": str(saved.seed_id),
                "skeleton_id": str(saved.id),
                "volume_count": len(saved.volumes),
            },
        )
        return saved

    def confirm_skeleton(self, skeleton_id: UUID) -> Skeleton:
        """将草稿骨架确认，确认后才能展开章节。"""
        skeleton = self._get_skeleton(skeleton_id)
        require_draft_skeleton(skeleton)
        now = datetime.now(UTC)
        skeleton.status = SkeletonStatus.CONFIRMED
        skeleton.confirmed_at = now
        skeleton.updated_at = now
        saved = self._repository.save_skeleton(skeleton)
        logger.info(
            "outline_skeleton_confirmed",
            extra={"skeleton_id": str(saved.id), "seed_id": str(saved.seed_id)},
        )
        return saved

    def expand_volume(self, skeleton_id: UUID, volume_id: UUID) -> list[ChapterSummary]:
        """在骨架确认后展开某个卷，并覆盖该卷旧章节摘要。"""
        skeleton = self._get_skeleton(skeleton_id)
        require_confirmed_skeleton(skeleton)
        volume = next((item for item in skeleton.volumes if item.id == volume_id), None)
        if volume is None:
            raise ValueError("骨架卷未找到")
        seed = self.get_seed(skeleton.seed_id)
        logger.info(
            "outline_volume_expansion_started",
            extra={"skeleton_id": str(skeleton.id), "volume_id": str(volume.id)},
        )
        summaries = self._ai_port.expand_volume(seed, skeleton, volume)
        now = datetime.now(UTC)
        for summary in summaries:
            summary.volume_id = volume.id
            summary.created_at = now
            summary.updated_at = now
            summary.is_stale = False
        # 重新展开卷会替换旧章节摘要，避免新旧摘要同时参与完整大纲聚合。
        saved = self._repository.save_chapter_summaries(summaries)
        logger.info(
            "outline_volume_expansion_completed",
            extra={
                "skeleton_id": str(skeleton.id),
                "volume_id": str(volume.id),
                "chapter_count": len(saved),
            },
        )
        return saved

    def update_volume(self, command: UpdateVolumeCommand):
        """更新骨架卷内容，并将该卷已展开章节标记为过期以提示重新展开。"""
        volume = self._repository.get_volume(command.volume_id)
        if volume is None:
            raise ValueError("骨架卷未找到")
        if command.title is not None:
            volume.title = command.title.strip()
        if command.turning_point is not None:
            volume.turning_point = command.turning_point.strip()
        volume.updated_at = datetime.now(UTC)
        updated = self._repository.update_skeleton_volume(volume)
        self._repository.mark_chapters_stale(updated.id)
        logger.info(
            "outline_volume_updated",
            extra={
                "volume_id": str(updated.id),
                "skeleton_id": str(updated.skeleton_id) if updated.skeleton_id else None,
            },
        )
        return updated

    def update_chapter(self, command: UpdateChapterCommand) -> ChapterSummary:
        """更新单个章节摘要标题或正文。"""
        chapter = self._repository.get_chapter_summary(command.chapter_id)
        if chapter is None:
            raise ValueError("章节摘要未找到")
        if command.title is not None:
            chapter.title = command.title.strip()
        if command.summary is not None:
            chapter.summary = command.summary.strip()
        chapter.updated_at = datetime.now(UTC)
        updated = self._repository.update_chapter_summary(chapter)
        logger.info(
            "outline_chapter_updated",
            extra={"chapter_id": str(updated.id), "volume_id": str(updated.volume_id)},
        )
        return updated

    def get_outline(self, seed_id: UUID) -> Outline:
        """聚合种子、骨架、卷和章节摘要，并计算完整性状态。"""
        seed = self.get_seed(seed_id)
        skeleton = self._repository.get_skeleton_by_seed(seed.id)
        if skeleton is None:
            raise ValueError("大纲未找到")
        chapters_by_volume = {
            volume.id: self._repository.get_chapters_by_volume(volume.id)
            for volume in skeleton.volumes
        }
        # 只有确认后的每个骨架卷都至少有一组章节摘要，聚合视图才算完整。
        is_complete = (
            skeleton.status is SkeletonStatus.CONFIRMED
            and bool(skeleton.volumes)
            and all(chapters_by_volume[volume.id] for volume in skeleton.volumes)
        )
        existing = self._repository.get_outline_by_seed(seed.id)
        outline = Outline(
            id=existing.id if existing is not None else uuid4(),
            seed=seed,
            skeleton=skeleton,
            chapters_by_volume=chapters_by_volume,
            status=OutlineStatus.COMPLETE if is_complete else OutlineStatus.IN_PROGRESS,
        )
        saved = self._repository.save_outline(outline)
        logger.info(
            "outline_view_built",
            extra={
                "seed_id": str(seed.id),
                "skeleton_id": str(skeleton.id),
                "status": saved.status.value,
                "volume_count": len(skeleton.volumes),
                "chapter_count": sum(len(chapters) for chapters in chapters_by_volume.values()),
            },
        )
        return saved

    def _get_skeleton(self, skeleton_id: UUID) -> Skeleton:
        skeleton = self._repository.get_skeleton(skeleton_id)
        if skeleton is None:
            raise ValueError("骨架未找到")
        return skeleton
