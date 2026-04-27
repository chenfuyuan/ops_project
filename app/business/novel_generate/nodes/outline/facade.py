"""大纲 node 对外稳定入口。

本模块位于 workflow / HTTP / bootstrap 与 outline 应用层之间，负责聚合各个
use case 的依赖并提供稳定调用面。facade 只做入口转发、轻量日志上下文和边界
异常协调，不承载骨架生成、卷展开、状态流转等具体业务规则。
"""

import logging
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

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class OutlineFacade:
    """聚合大纲节点的应用服务并暴露稳定业务入口。

    bootstrap 负责注入所有 use case 与 repository 实现；调用方无需了解应用层和
    基础设施层的内部拆分。方法只记录安全的资源标识和结果摘要，不记录创作种子、
    prompt、章节摘要等可能包含用户内容的完整文本。
    """

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
        """接收已装配好的应用服务，保持 facade 本身不做实现选择。"""
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
        """创建大纲种子并返回保存后的领域实体。

        command 中包含作者输入的创作内容，facade 层不直接记录字段值；具体校验、
        时间戳填充和持久化由 CreateSeedUseCase 完成。
        """
        logger.debug("outline_facade_create_seed_dispatched")
        return self._create_seed.execute(command)

    def get_seed(self, seed_id: UUID) -> Seed:
        """按 seed_id 读取创作种子，未找到时由用例抛出业务错误。"""
        logger.debug(
            "outline_facade_get_seed_dispatched", extra={"seed_id": str(seed_id)}
        )
        return self._get_seed.execute(seed_id)

    def generate_skeleton(self, seed_id: UUID) -> Skeleton:
        """为指定 seed 生成新的骨架草稿。"""
        logger.debug(
            "outline_facade_generate_skeleton_dispatched",
            extra={"seed_id": str(seed_id)},
        )
        return self._generate_skeleton.execute(seed_id)

    def get_skeleton(self, skeleton_id: UUID) -> Skeleton:
        """按 skeleton_id 读取骨架实体。

        这是 facade 中唯一直接读取 repository 的查询方法，因此在这里记录未命中和
        命中结果；其他业务行为的日志由对应 use case 或 adapter 负责。
        """
        skeleton = self._repository.get_skeleton(skeleton_id)
        if skeleton is None:
            logger.warning(
                "outline_skeleton_not_found",
                extra={"skeleton_id": str(skeleton_id), "stage": "facade_get_skeleton"},
            )
            raise ValueError("骨架未找到")
        logger.debug(
            "outline_skeleton_loaded",
            extra={
                "skeleton_id": str(skeleton.id),
                "seed_id": str(skeleton.seed_id),
                "status": skeleton.status.value,
                "volume_count": len(skeleton.volumes),
            },
        )
        return skeleton

    def confirm_skeleton(self, skeleton_id: UUID) -> Skeleton:
        """确认骨架草稿，确认后才允许展开卷章节。"""
        logger.debug(
            "outline_facade_confirm_skeleton_dispatched",
            extra={"skeleton_id": str(skeleton_id)},
        )
        return self._confirm_skeleton.execute(skeleton_id)

    def expand_volume(self, skeleton_id: UUID, volume_id: UUID) -> list[ChapterSummary]:
        """展开已确认骨架中的单个卷并返回章节摘要列表。"""
        logger.debug(
            "outline_facade_expand_volume_dispatched",
            extra={"skeleton_id": str(skeleton_id), "volume_id": str(volume_id)},
        )
        return self._expand_volume.execute(skeleton_id, volume_id)

    def update_volume(self, command: UpdateVolumeCommand) -> SkeletonVolume:
        """更新骨架卷标题或转折点，并触发既有章节摘要过期标记。"""
        logger.debug(
            "outline_facade_update_volume_dispatched",
            extra={"volume_id": str(command.volume_id)},
        )
        return self._update_volume.execute(command)

    def update_chapter(self, command: UpdateChapterCommand) -> ChapterSummary:
        """更新单个章节摘要的标题或摘要正文。"""
        logger.debug(
            "outline_facade_update_chapter_dispatched",
            extra={"chapter_id": str(command.chapter_id)},
        )
        return self._update_chapter.execute(command)

    def get_outline(self, seed_id: UUID) -> Outline:
        """构建并读取 seed 维度的大纲聚合视图。"""
        logger.debug(
            "outline_facade_get_outline_dispatched", extra={"seed_id": str(seed_id)}
        )
        return self._get_outline.execute(seed_id)
