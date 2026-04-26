import unittest
from uuid import UUID

from app.business.novel_generate.nodes.outline.application.dto import (
    CreateSeedCommand,
    UpdateChapterCommand,
    UpdateVolumeCommand,
)
from app.business.novel_generate.nodes.outline.application.use_cases.confirm_skeleton import (
    ConfirmSkeletonUseCase,
)
from app.business.novel_generate.nodes.outline.application.use_cases.create_seed import (
    CreateSeedUseCase,
)
from app.business.novel_generate.nodes.outline.application.use_cases.expand_volume import (
    ExpandVolumeUseCase,
)
from app.business.novel_generate.nodes.outline.application.use_cases.generate_skeleton import (
    GenerateSkeletonUseCase,
)
from app.business.novel_generate.nodes.outline.application.use_cases.get_outline import (
    GetOutlineUseCase,
)
from app.business.novel_generate.nodes.outline.application.use_cases.get_seed import (
    GetSeedUseCase,
)
from app.business.novel_generate.nodes.outline.application.use_cases.update_chapter import (
    UpdateChapterUseCase,
)
from app.business.novel_generate.nodes.outline.application.use_cases.update_volume import (
    UpdateVolumeUseCase,
)
from app.business.novel_generate.nodes.outline.domain.models import (
    ChapterSummary,
    Outline,
    OutlineStatus,
    Seed,
    Skeleton,
    SkeletonStatus,
    SkeletonVolume,
)
from app.business.novel_generate.nodes.outline.facade import OutlineFacade


class InMemoryOutlineRepository:
    def __init__(self) -> None:
        self.seeds: dict[UUID, Seed] = {}
        self.skeletons: dict[UUID, Skeleton] = {}
        self.skeleton_by_seed: dict[UUID, UUID] = {}
        self.chapters: dict[UUID, ChapterSummary] = {}
        self.chapters_by_volume: dict[UUID, list[UUID]] = {}
        self.outlines_by_seed: dict[UUID, Outline] = {}

    def save_seed(self, seed: Seed) -> Seed:
        self.seeds[seed.id] = seed
        return seed

    def get_seed(self, seed_id: UUID) -> Seed | None:
        return self.seeds.get(seed_id)

    def save_skeleton(self, skeleton: Skeleton) -> Skeleton:
        old_id = self.skeleton_by_seed.get(skeleton.seed_id)
        if old_id is not None:
            old = self.skeletons.pop(old_id, None)
            if old is not None:
                for volume in old.volumes:
                    self.delete_chapters_by_volume(volume.id)
                    self.chapters_by_volume.pop(volume.id, None)
        self.skeletons[skeleton.id] = skeleton
        self.skeleton_by_seed[skeleton.seed_id] = skeleton.id
        return skeleton

    def get_skeleton(self, skeleton_id: UUID) -> Skeleton | None:
        return self.skeletons.get(skeleton_id)

    def get_skeleton_by_seed(self, seed_id: UUID) -> Skeleton | None:
        skeleton_id = self.skeleton_by_seed.get(seed_id)
        if skeleton_id is None:
            return None
        return self.skeletons.get(skeleton_id)

    def get_volume(self, volume_id: UUID) -> SkeletonVolume | None:
        for skeleton in self.skeletons.values():
            for volume in skeleton.volumes:
                if volume.id == volume_id:
                    return volume
        return None

    def get_chapter_summary(self, chapter_id: UUID) -> ChapterSummary | None:
        return self.chapters.get(chapter_id)

    def save_chapter_summaries(
        self, summaries: list[ChapterSummary]
    ) -> list[ChapterSummary]:
        if summaries:
            self.delete_chapters_by_volume(summaries[0].volume_id)
        for summary in summaries:
            self.chapters[summary.id] = summary
            self.chapters_by_volume.setdefault(summary.volume_id, []).append(summary.id)
        return summaries

    def get_chapters_by_volume(self, volume_id: UUID) -> list[ChapterSummary]:
        return [
            self.chapters[chapter_id]
            for chapter_id in self.chapters_by_volume.get(volume_id, [])
        ]

    def delete_chapters_by_volume(self, volume_id: UUID) -> None:
        for chapter_id in self.chapters_by_volume.pop(volume_id, []):
            self.chapters.pop(chapter_id, None)

    def mark_chapters_stale(self, volume_id: UUID) -> None:
        for chapter in self.get_chapters_by_volume(volume_id):
            chapter.is_stale = True

    def update_skeleton_volume(self, volume: SkeletonVolume) -> SkeletonVolume:
        return volume

    def update_chapter_summary(self, chapter: ChapterSummary) -> ChapterSummary:
        self.chapters[chapter.id] = chapter
        return chapter

    def save_outline(self, outline: Outline) -> Outline:
        self.outlines_by_seed[outline.seed_id] = outline
        return outline

    def get_outline_by_seed(self, seed_id: UUID) -> Outline | None:
        return self.outlines_by_seed.get(seed_id)


class StubOutlineAiPort:
    def __init__(self) -> None:
        self.skeleton_titles = ["开端", "对抗", "终局"]
        self.chapter_titles = ["第一章", "第二章"]

    def generate_skeleton(self, seed: Seed) -> list[SkeletonVolume]:
        return [
            SkeletonVolume(
                skeleton_id=None,
                sequence=index,
                title=title,
                turning_point=f"{title}转折",
            )
            for index, title in enumerate(self.skeleton_titles, start=1)
        ]

    def expand_volume(
        self, seed: Seed, skeleton: Skeleton, volume: SkeletonVolume
    ) -> list[ChapterSummary]:
        return [
            ChapterSummary(
                volume_id=volume.id,
                sequence=index,
                title=title,
                summary=f"{title}摘要",
            )
            for index, title in enumerate(self.chapter_titles, start=1)
        ]


class OutlineFacadeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = InMemoryOutlineRepository()
        self.ai_port = StubOutlineAiPort()
        get_seed = GetSeedUseCase(self.repository)
        self.facade = OutlineFacade(
            create_seed=CreateSeedUseCase(self.repository),
            get_seed=get_seed,
            generate_skeleton=GenerateSkeletonUseCase(
                self.repository, self.ai_port, get_seed
            ),
            confirm_skeleton=ConfirmSkeletonUseCase(self.repository),
            expand_volume=ExpandVolumeUseCase(self.repository, self.ai_port, get_seed),
            update_volume=UpdateVolumeUseCase(self.repository),
            update_chapter=UpdateChapterUseCase(self.repository),
            get_outline=GetOutlineUseCase(self.repository, get_seed),
            repository=self.repository,
        )

    def _seed_command(self) -> CreateSeedCommand:
        return CreateSeedCommand(
            title="群星回声",
            genre="科幻",
            protagonist="失忆领航员",
            core_conflict="殖民舰队争夺唯一航道",
            story_direction="主角逐步发现自己曾关闭航道",
            additional_notes="偏群像",
        )

    def _create_seed(self) -> Seed:
        return self.facade.create_seed(self._seed_command())

    def _confirmed_skeleton(self) -> Skeleton:
        seed = self._create_seed()
        skeleton = self.facade.generate_skeleton(seed.id)
        return self.facade.confirm_skeleton(skeleton.id)

    def test_create_seed_persists_complete_seed(self) -> None:
        seed = self.facade.create_seed(self._seed_command())

        self.assertEqual("群星回声", seed.title)
        self.assertEqual(seed, self.repository.get_seed(seed.id))

    def test_create_seed_rejects_missing_required_field(self) -> None:
        with self.assertRaisesRegex(ValueError, "title"):
            self.facade.create_seed(
                CreateSeedCommand(
                    title=" ",
                    genre="科幻",
                    protagonist="失忆领航员",
                    core_conflict="殖民舰队争夺唯一航道",
                    story_direction="主角逐步发现自己曾关闭航道",
                )
            )

    def test_generate_skeleton_creates_draft_skeleton_and_replaces_existing_one(
        self,
    ) -> None:
        seed = self._create_seed()
        first = self.facade.generate_skeleton(seed.id)
        self.ai_port.skeleton_titles = ["新开端", "新终局"]

        second = self.facade.generate_skeleton(seed.id)

        self.assertEqual(SkeletonStatus.DRAFT, first.status)
        self.assertEqual(SkeletonStatus.DRAFT, second.status)
        self.assertNotEqual(first.id, second.id)
        self.assertEqual(
            ["新开端", "新终局"], [volume.title for volume in second.volumes]
        )
        self.assertEqual(second, self.repository.get_skeleton_by_seed(seed.id))

    def test_get_skeleton_returns_existing_skeleton(self) -> None:
        seed = self._create_seed()
        skeleton = self.facade.generate_skeleton(seed.id)

        self.assertEqual(skeleton, self.facade.get_skeleton(skeleton.id))

    def test_confirm_skeleton_requires_draft_status(self) -> None:
        skeleton = self._confirmed_skeleton()

        self.assertEqual(SkeletonStatus.CONFIRMED, skeleton.status)
        self.assertIsNotNone(skeleton.confirmed_at)
        with self.assertRaisesRegex(ValueError, "已确认"):
            self.facade.confirm_skeleton(skeleton.id)

    def test_expand_volume_requires_confirmed_skeleton_and_replaces_existing_chapters(
        self,
    ) -> None:
        seed = self._create_seed()
        draft = self.facade.generate_skeleton(seed.id)

        with self.assertRaisesRegex(ValueError, "骨架未确认"):
            self.facade.expand_volume(draft.id, draft.volumes[0].id)

        confirmed = self.facade.confirm_skeleton(draft.id)
        first = self.facade.expand_volume(confirmed.id, confirmed.volumes[0].id)
        self.ai_port.chapter_titles = ["重写章"]
        second = self.facade.expand_volume(confirmed.id, confirmed.volumes[0].id)

        self.assertEqual(["第一章", "第二章"], [chapter.title for chapter in first])
        self.assertEqual(["重写章"], [chapter.title for chapter in second])
        self.assertEqual(
            second, self.repository.get_chapters_by_volume(confirmed.volumes[0].id)
        )

    def test_update_volume_marks_existing_chapters_stale(self) -> None:
        skeleton = self._confirmed_skeleton()
        self.facade.expand_volume(skeleton.id, skeleton.volumes[0].id)

        updated = self.facade.update_volume(
            UpdateVolumeCommand(
                volume_id=skeleton.volumes[0].id,
                title="改写卷",
                turning_point="新的核心转折",
            )
        )

        self.assertEqual("改写卷", updated.title)
        self.assertTrue(
            all(
                chapter.is_stale
                for chapter in self.repository.get_chapters_by_volume(updated.id)
            )
        )

    def test_update_chapter_changes_title_and_summary(self) -> None:
        skeleton = self._confirmed_skeleton()
        chapters = self.facade.expand_volume(skeleton.id, skeleton.volumes[0].id)

        updated = self.facade.update_chapter(
            UpdateChapterCommand(
                chapter_id=chapters[0].id,
                title="改写章",
                summary="改写摘要",
            )
        )

        self.assertEqual("改写章", updated.title)
        self.assertEqual("改写摘要", updated.summary)

    def test_get_outline_reports_complete_only_when_all_volumes_are_expanded(
        self,
    ) -> None:
        seed = self._create_seed()

        with self.assertRaisesRegex(ValueError, "大纲未找到"):
            self.facade.get_outline(seed.id)

        skeleton = self.facade.confirm_skeleton(
            self.facade.generate_skeleton(seed.id).id
        )
        partial = self.facade.expand_volume(skeleton.id, skeleton.volumes[0].id)
        outline = self.facade.get_outline(seed.id)

        self.assertEqual(OutlineStatus.IN_PROGRESS, outline.status)
        self.assertEqual(partial, outline.chapters_by_volume[skeleton.volumes[0].id])
        self.assertEqual([], outline.chapters_by_volume[skeleton.volumes[1].id])

        for volume in skeleton.volumes[1:]:
            self.facade.expand_volume(skeleton.id, volume.id)

        complete = self.facade.get_outline(seed.id)

        self.assertEqual(OutlineStatus.COMPLETE, complete.status)


if __name__ == "__main__":
    unittest.main()
