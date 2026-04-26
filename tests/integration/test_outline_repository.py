import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.business.novel_generate.nodes.outline.entities import (
    ChapterSummary,
    Seed,
    Skeleton,
    Outline,
    OutlineStatus,
    SkeletonStatus,
    SkeletonVolume,
)
from app.business.novel_generate.nodes.outline.infrastructure.repository import (
    Base,
    OutlineRepositoryImpl,
)


class OutlineRepositoryImplTest(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.repository = OutlineRepositoryImpl(sessionmaker(bind=self.engine))

    def test_persists_seed_skeleton_volume_and_chapter_lifecycle(self) -> None:
        seed = self.repository.save_seed(
            Seed(
                title="群星回声",
                genre="科幻",
                protagonist="失忆领航员",
                core_conflict="殖民舰队争夺唯一航道",
                story_direction="主角发现真相",
            )
        )
        volume = SkeletonVolume(
            skeleton_id=None,
            sequence=1,
            title="开端",
            turning_point="发现航道",
        )
        skeleton = Skeleton(seed_id=seed.id, volumes=[volume])
        volume.skeleton_id = skeleton.id

        saved_skeleton = self.repository.save_skeleton(skeleton)
        saved_chapters = self.repository.save_chapter_summaries(
            [
                ChapterSummary(
                    volume_id=saved_skeleton.volumes[0].id,
                    sequence=1,
                    title="第一章",
                    summary="启程",
                )
            ]
        )
        self.repository.mark_chapters_stale(saved_skeleton.volumes[0].id)

        loaded_seed = self.repository.get_seed(seed.id)
        loaded_skeleton = self.repository.get_skeleton_by_seed(seed.id)
        loaded_chapters = self.repository.get_chapters_by_volume(saved_skeleton.volumes[0].id)

        self.assertEqual("群星回声", loaded_seed.title)
        self.assertEqual(SkeletonStatus.DRAFT, loaded_skeleton.status)
        self.assertEqual("开端", loaded_skeleton.volumes[0].title)
        self.assertEqual(saved_chapters[0].id, loaded_chapters[0].id)
        self.assertTrue(loaded_chapters[0].is_stale)

    def test_persists_outline_record_for_seed(self) -> None:
        seed = self.repository.save_seed(
            Seed(
                title="群星回声",
                genre="科幻",
                protagonist="失忆领航员",
                core_conflict="殖民舰队争夺唯一航道",
                story_direction="主角发现真相",
            )
        )
        volume = SkeletonVolume(
            skeleton_id=None,
            sequence=1,
            title="开端",
            turning_point="发现航道",
        )
        skeleton = Skeleton(seed_id=seed.id, volumes=[volume])
        volume.skeleton_id = skeleton.id
        self.repository.save_skeleton(skeleton)
        outline = Outline(
            seed=seed,
            skeleton=skeleton,
            chapters_by_volume={volume.id: []},
            status=OutlineStatus.IN_PROGRESS,
        )

        saved = self.repository.save_outline(outline)
        loaded = self.repository.get_outline_by_seed(seed.id)

        self.assertEqual(saved.id, loaded.id)
        self.assertEqual(seed.id, loaded.seed_id)
        self.assertEqual(skeleton.id, loaded.skeleton_id)
        self.assertEqual(OutlineStatus.IN_PROGRESS, loaded.status)

    def test_saving_new_skeleton_for_seed_replaces_old_volumes_and_chapters(self) -> None:
        seed = self.repository.save_seed(
            Seed(
                title="群星回声",
                genre="科幻",
                protagonist="失忆领航员",
                core_conflict="殖民舰队争夺唯一航道",
                story_direction="主角发现真相",
            )
        )
        old_volume = SkeletonVolume(
            skeleton_id=None,
            sequence=1,
            title="旧开端",
            turning_point="旧转折",
        )
        old_skeleton = Skeleton(seed_id=seed.id, volumes=[old_volume])
        old_volume.skeleton_id = old_skeleton.id
        self.repository.save_skeleton(old_skeleton)
        self.repository.save_chapter_summaries(
            [
                ChapterSummary(
                    volume_id=old_volume.id,
                    sequence=1,
                    title="旧章节",
                    summary="旧摘要",
                )
            ]
        )
        new_volume = SkeletonVolume(
            skeleton_id=None,
            sequence=1,
            title="新开端",
            turning_point="新转折",
        )
        new_skeleton = Skeleton(seed_id=seed.id, volumes=[new_volume])
        new_volume.skeleton_id = new_skeleton.id

        saved = self.repository.save_skeleton(new_skeleton)

        self.assertEqual(saved.id, self.repository.get_skeleton_by_seed(seed.id).id)
        self.assertEqual("新开端", self.repository.get_volume(new_volume.id).title)
        self.assertEqual([], self.repository.get_chapters_by_volume(old_volume.id))


if __name__ == "__main__":
    unittest.main()
