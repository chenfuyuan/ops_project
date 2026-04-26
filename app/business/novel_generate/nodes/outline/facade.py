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
    Seed,
    Skeleton,
    SkeletonVolume,
)
from app.business.novel_generate.nodes.outline.domain.repositories import (
    OutlineRepository,
)


class OutlineFacade:
    def __init__(
        self,
        create_seed: CreateSeedUseCase,
        get_seed: GetSeedUseCase,
        generate_skeleton: GenerateSkeletonUseCase,
        confirm_skeleton: ConfirmSkeletonUseCase,
        expand_volume: ExpandVolumeUseCase,
        update_volume: UpdateVolumeUseCase,
        update_chapter: UpdateChapterUseCase,
        get_outline: GetOutlineUseCase,
        repository: OutlineRepository,
    ) -> None:
        self._create_seed = create_seed
        self._get_seed = get_seed
        self._generate_skeleton = generate_skeleton
        self._confirm_skeleton = confirm_skeleton
        self._expand_volume = expand_volume
        self._update_volume = update_volume
        self._update_chapter = update_chapter
        self._get_outline = get_outline
        self._repository = repository

    def create_seed(self, command: CreateSeedCommand) -> Seed:
        return self._create_seed.execute(command)

    def get_seed(self, seed_id: UUID) -> Seed:
        return self._get_seed.execute(seed_id)

    def generate_skeleton(self, seed_id: UUID) -> Skeleton:
        return self._generate_skeleton.execute(seed_id)

    def get_skeleton(self, skeleton_id: UUID) -> Skeleton:
        skeleton = self._repository.get_skeleton(skeleton_id)
        if skeleton is None:
            raise ValueError("骨架未找到")
        return skeleton

    def confirm_skeleton(self, skeleton_id: UUID) -> Skeleton:
        return self._confirm_skeleton.execute(skeleton_id)

    def expand_volume(self, skeleton_id: UUID, volume_id: UUID) -> list[ChapterSummary]:
        return self._expand_volume.execute(skeleton_id, volume_id)

    def update_volume(self, command: UpdateVolumeCommand) -> SkeletonVolume:
        return self._update_volume.execute(command)

    def update_chapter(self, command: UpdateChapterCommand) -> ChapterSummary:
        return self._update_chapter.execute(command)

    def get_outline(self, seed_id: UUID) -> Outline:
        return self._get_outline.execute(seed_id)
