"""大纲应用层外部能力端口。"""

from typing import Protocol

from app.business.novel_generate.nodes.outline.domain.models import (
    ChapterSummary,
    Seed,
    Skeleton,
    SkeletonVolume,
)


class OutlineAiPort(Protocol):
    def generate_skeleton(self, seed: Seed) -> list[SkeletonVolume]: ...

    def expand_volume(
        self, seed: Seed, skeleton: Skeleton, volume: SkeletonVolume
    ) -> list[ChapterSummary]: ...
