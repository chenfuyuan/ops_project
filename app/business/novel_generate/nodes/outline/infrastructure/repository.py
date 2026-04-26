"""大纲节点 SQLAlchemy repository 实现。

本模块负责业务实体与数据库 record 的双向转换，并把替换、删除、
过期标记等持久化副作用限制在 repository 边界内。
"""

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from app.business.novel_generate.nodes.outline.entities import (
    ChapterSummary,
    Outline,
    OutlineStatus,
    Seed,
    Skeleton,
    SkeletonStatus,
    SkeletonVolume,
)
from app.business.novel_generate.nodes.outline.ports import OutlineRepository


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Base(DeclarativeBase):
    """大纲节点 SQLAlchemy metadata 根对象，供迁移和测试创建表结构。"""


class OutlineSeedRecord(Base):
    """持久化作者创作种子，字段内容不应进入运行时日志。"""

    __tablename__ = "outline_seeds"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    genre: Mapped[str] = mapped_column(String(50), nullable=False)
    protagonist: Mapped[str] = mapped_column(Text, nullable=False)
    core_conflict: Mapped[str] = mapped_column(Text, nullable=False)
    story_direction: Mapped[str] = mapped_column(Text, nullable=False)
    additional_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class OutlineSkeletonRecord(Base):
    """持久化 seed 当前骨架，seed_id 唯一约束保证单 seed 单当前骨架。"""

    __tablename__ = "outline_skeletons"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    seed_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("outline_seeds.id"), nullable=False, unique=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    volumes: Mapped[list["OutlineSkeletonVolumeRecord"]] = relationship(
        cascade="all, delete-orphan",
        order_by="OutlineSkeletonVolumeRecord.sequence",
    )


class OutlineSkeletonVolumeRecord(Base):
    """持久化骨架卷，随所属 skeleton 级联删除。"""

    __tablename__ = "outline_skeleton_volumes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    skeleton_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("outline_skeletons.id", ondelete="CASCADE"), nullable=False
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    turning_point: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    chapters: Mapped[list["OutlineChapterSummaryRecord"]] = relationship(
        cascade="all, delete-orphan",
        order_by="OutlineChapterSummaryRecord.sequence",
    )


class OutlineChapterSummaryRecord(Base):
    """持久化章节摘要，随所属 volume 级联删除。"""

    __tablename__ = "outline_chapter_summaries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    volume_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("outline_skeleton_volumes.id", ondelete="CASCADE"),
        nullable=False,
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    is_stale: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class OutlineRecord(Base):
    """持久化 seed 维度的大纲聚合状态。"""

    __tablename__ = "outlines"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    seed_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("outline_seeds.id"), nullable=False, unique=True
    )
    skeleton_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("outline_skeletons.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class OutlineRepositoryImpl(OutlineRepository):
    """使用 SQLAlchemy session factory 持久化大纲实体并管理事务边界。"""

    def __init__(self, session_factory: sessionmaker) -> None:
        """接收由 bootstrap 创建的 session factory，避免 repository 自行读取配置。"""
        self._session_factory = session_factory

    def save_seed(self, seed: Seed) -> Seed:
        """保存结构化创作种子，提交后返回原业务实体。"""
        with self._session_factory() as session:
            session.merge(self._seed_record(seed))
            session.commit()
        logger.info("outline_seed_saved", extra={"seed_id": str(seed.id)})
        return seed

    def get_seed(self, seed_id: UUID) -> Seed | None:
        """按 ID 读取创作种子，未找到时返回 None。"""
        with self._session_factory() as session:
            record = session.get(OutlineSeedRecord, str(seed_id))
            return self._seed_entity(record) if record is not None else None

    def save_skeleton(self, skeleton: Skeleton) -> Skeleton:
        """保存骨架；同一 seed 只能保留一个当前骨架。"""
        with self._session_factory() as session:
            existing = session.scalar(
                select(OutlineSkeletonRecord).where(
                    OutlineSkeletonRecord.seed_id == str(skeleton.seed_id)
                )
            )
            if existing is not None and existing.id != str(skeleton.id):
                # 新骨架会使旧 outline 聚合失效，先删除聚合记录再删除旧骨架。
                existing_outline = session.scalar(
                    select(OutlineRecord).where(
                        OutlineRecord.seed_id == str(skeleton.seed_id)
                    )
                )
                if existing_outline is not None:
                    session.delete(existing_outline)
                    session.flush()
                session.delete(existing)
                session.flush()
            session.merge(self._skeleton_record(skeleton))
            session.commit()
        logger.info(
            "outline_skeleton_saved",
            extra={
                "seed_id": str(skeleton.seed_id),
                "skeleton_id": str(skeleton.id),
                "volume_count": len(skeleton.volumes),
            },
        )
        return skeleton

    def get_skeleton(self, skeleton_id: UUID) -> Skeleton | None:
        """按 ID 读取骨架及其卷列表，未找到时返回 None。"""
        with self._session_factory() as session:
            record = session.get(OutlineSkeletonRecord, str(skeleton_id))
            return self._skeleton_entity(record) if record is not None else None

    def get_skeleton_by_seed(self, seed_id: UUID) -> Skeleton | None:
        """读取某个 seed 当前生效骨架，未生成时返回 None。"""
        with self._session_factory() as session:
            record = session.scalar(
                select(OutlineSkeletonRecord).where(
                    OutlineSkeletonRecord.seed_id == str(seed_id)
                )
            )
            return self._skeleton_entity(record) if record is not None else None

    def get_volume(self, volume_id: UUID) -> SkeletonVolume | None:
        """按 ID 读取骨架卷，未找到时返回 None。"""
        with self._session_factory() as session:
            record = session.get(OutlineSkeletonVolumeRecord, str(volume_id))
            return self._volume_entity(record) if record is not None else None

    def get_chapter_summary(self, chapter_id: UUID) -> ChapterSummary | None:
        """按 ID 读取章节摘要，未找到时返回 None。"""
        with self._session_factory() as session:
            record = session.get(OutlineChapterSummaryRecord, str(chapter_id))
            return self._chapter_entity(record) if record is not None else None

    def save_chapter_summaries(
        self, summaries: list[ChapterSummary]
    ) -> list[ChapterSummary]:
        """替换目标卷下的章节摘要，避免旧摘要继续参与大纲聚合。"""
        with self._session_factory() as session:
            if summaries:
                # 卷重新展开后只保留最新章节摘要。
                self._delete_chapters_by_volume(session, summaries[0].volume_id)
            for summary in summaries:
                session.add(self._chapter_record(summary))
            session.commit()
        if summaries:
            logger.info(
                "outline_chapter_summaries_saved",
                extra={
                    "volume_id": str(summaries[0].volume_id),
                    "chapter_count": len(summaries),
                },
            )
        return summaries

    def get_chapters_by_volume(self, volume_id: UUID) -> list[ChapterSummary]:
        """按章节序号读取某个卷下的章节摘要。"""
        with self._session_factory() as session:
            records = session.scalars(
                select(OutlineChapterSummaryRecord)
                .where(OutlineChapterSummaryRecord.volume_id == str(volume_id))
                .order_by(OutlineChapterSummaryRecord.sequence)
            ).all()
            return [self._chapter_entity(record) for record in records]

    def delete_chapters_by_volume(self, volume_id: UUID) -> None:
        """删除某个卷下的章节摘要，用于显式清理或替换前清理。"""
        with self._session_factory() as session:
            self._delete_chapters_by_volume(session, volume_id)
            session.commit()
        logger.info("outline_chapters_deleted", extra={"volume_id": str(volume_id)})

    def mark_chapters_stale(self, volume_id: UUID) -> None:
        """将章节摘要标记为过期而不删除，保留作者可见的历史展开结果。"""
        with self._session_factory() as session:
            records = session.scalars(
                select(OutlineChapterSummaryRecord).where(
                    OutlineChapterSummaryRecord.volume_id == str(volume_id)
                )
            ).all()
            for record in records:
                record.is_stale = True
            session.commit()
        logger.info(
            "outline_chapters_marked_stale",
            extra={"volume_id": str(volume_id), "chapter_count": len(records)},
        )

    def update_skeleton_volume(self, volume: SkeletonVolume) -> SkeletonVolume:
        """保存作者对骨架卷标题或转折点的编辑。"""
        with self._session_factory() as session:
            record = session.get(OutlineSkeletonVolumeRecord, str(volume.id))
            if record is None:
                raise ValueError("骨架卷未找到")
            record.title = volume.title
            record.turning_point = volume.turning_point
            record.updated_at = volume.updated_at
            session.commit()
        logger.info(
            "outline_volume_saved",
            extra={
                "volume_id": str(volume.id),
                "skeleton_id": str(volume.skeleton_id) if volume.skeleton_id else None,
            },
        )
        return volume

    def update_chapter_summary(self, chapter: ChapterSummary) -> ChapterSummary:
        """保存作者对单个章节标题或摘要的编辑。"""
        with self._session_factory() as session:
            record = session.get(OutlineChapterSummaryRecord, str(chapter.id))
            if record is None:
                raise ValueError("章节摘要未找到")
            record.title = chapter.title
            record.summary = chapter.summary
            record.updated_at = chapter.updated_at
            session.commit()
        logger.info(
            "outline_chapter_saved",
            extra={"chapter_id": str(chapter.id), "volume_id": str(chapter.volume_id)},
        )
        return chapter

    def save_outline(self, outline: Outline) -> Outline:
        """保存 seed 维度的大纲聚合视图状态。"""
        with self._session_factory() as session:
            session.merge(self._outline_record(outline))
            session.commit()
        logger.info(
            "outline_saved",
            extra={
                "seed_id": str(outline.seed_id),
                "skeleton_id": str(outline.skeleton_id),
                "status": outline.status.value,
            },
        )
        return outline

    def get_outline_by_seed(self, seed_id: UUID) -> Outline | None:
        """读取 seed 维度的大纲聚合视图，缺少关联记录时返回 None。"""
        with self._session_factory() as session:
            record = session.scalar(
                select(OutlineRecord).where(OutlineRecord.seed_id == str(seed_id))
            )
            if record is None:
                return None
            seed = session.get(OutlineSeedRecord, record.seed_id)
            skeleton = session.get(OutlineSkeletonRecord, record.skeleton_id)
            if seed is None or skeleton is None:
                return None
            chapters_by_volume = {
                UUID(volume.id): [
                    self._chapter_entity(chapter)
                    for chapter in sorted(volume.chapters, key=lambda item: item.sequence)
                ]
                for volume in skeleton.volumes
            }
            return Outline(
                id=UUID(record.id),
                seed=self._seed_entity(seed),
                skeleton=self._skeleton_entity(skeleton),
                chapters_by_volume=chapters_by_volume,
                status=OutlineStatus(record.status),
                created_at=record.created_at,
                updated_at=record.updated_at,
            )

    def _delete_chapters_by_volume(self, session, volume_id: UUID) -> None:
        records = session.scalars(
            select(OutlineChapterSummaryRecord).where(
                OutlineChapterSummaryRecord.volume_id == str(volume_id)
            )
        ).all()
        for record in records:
            session.delete(record)

    # 以下 mapper 只做数据库形状和业务实体之间的转换，不承载业务决策。
    def _seed_record(self, seed: Seed) -> OutlineSeedRecord:
        return OutlineSeedRecord(
            id=str(seed.id),
            title=seed.title,
            genre=seed.genre,
            protagonist=seed.protagonist,
            core_conflict=seed.core_conflict,
            story_direction=seed.story_direction,
            additional_notes=seed.additional_notes,
            created_at=seed.created_at,
            updated_at=seed.updated_at,
        )

    def _skeleton_record(self, skeleton: Skeleton) -> OutlineSkeletonRecord:
        return OutlineSkeletonRecord(
            id=str(skeleton.id),
            seed_id=str(skeleton.seed_id),
            status=skeleton.status.value,
            created_at=skeleton.created_at,
            updated_at=skeleton.updated_at,
            confirmed_at=skeleton.confirmed_at,
            volumes=[self._volume_record(volume) for volume in skeleton.volumes],
        )

    def _volume_record(self, volume: SkeletonVolume) -> OutlineSkeletonVolumeRecord:
        return OutlineSkeletonVolumeRecord(
            id=str(volume.id),
            skeleton_id=str(volume.skeleton_id),
            sequence=volume.sequence,
            title=volume.title,
            turning_point=volume.turning_point,
            created_at=volume.created_at,
            updated_at=volume.updated_at,
        )

    def _chapter_record(self, chapter: ChapterSummary) -> OutlineChapterSummaryRecord:
        return OutlineChapterSummaryRecord(
            id=str(chapter.id),
            volume_id=str(chapter.volume_id),
            sequence=chapter.sequence,
            title=chapter.title,
            summary=chapter.summary,
            is_stale=chapter.is_stale,
            created_at=chapter.created_at,
            updated_at=chapter.updated_at,
        )

    def _outline_record(self, outline: Outline) -> OutlineRecord:
        return OutlineRecord(
            id=str(outline.id),
            seed_id=str(outline.seed_id),
            skeleton_id=str(outline.skeleton_id),
            status=outline.status.value,
            created_at=outline.created_at,
            updated_at=outline.updated_at,
        )

    def _seed_entity(self, record: OutlineSeedRecord) -> Seed:
        return Seed(
            id=UUID(record.id),
            title=record.title,
            genre=record.genre,
            protagonist=record.protagonist,
            core_conflict=record.core_conflict,
            story_direction=record.story_direction,
            additional_notes=record.additional_notes,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    def _skeleton_entity(self, record: OutlineSkeletonRecord) -> Skeleton:
        return Skeleton(
            id=UUID(record.id),
            seed_id=UUID(record.seed_id),
            status=SkeletonStatus(record.status),
            volumes=[self._volume_entity(volume) for volume in record.volumes],
            created_at=record.created_at,
            updated_at=record.updated_at,
            confirmed_at=record.confirmed_at,
        )

    def _volume_entity(self, record: OutlineSkeletonVolumeRecord) -> SkeletonVolume:
        return SkeletonVolume(
            id=UUID(record.id),
            skeleton_id=UUID(record.skeleton_id),
            sequence=record.sequence,
            title=record.title,
            turning_point=record.turning_point,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    def _chapter_entity(self, record: OutlineChapterSummaryRecord) -> ChapterSummary:
        return ChapterSummary(
            id=UUID(record.id),
            volume_id=UUID(record.volume_id),
            sequence=record.sequence,
            title=record.title,
            summary=record.summary,
            is_stale=record.is_stale,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )
