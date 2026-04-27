"""生成大纲骨架用例。

该用例串联 Seed 读取、AI 骨架生成、领域实体补齐与持久化。AI prompt 和模型输出
可能包含作者创作内容，因此日志仅记录 seed_id、skeleton_id、状态和数量摘要。
"""

import logging
from datetime import UTC, datetime
from uuid import UUID

from app.business.novel_generate.nodes.outline.application.ports import OutlineAiPort
from app.business.novel_generate.nodes.outline.application.use_cases.get_seed import (
    GetSeedUseCase,
)
from app.business.novel_generate.nodes.outline.domain.models import Skeleton
from app.business.novel_generate.nodes.outline.domain.repositories import (
    OutlineRepository,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class GenerateSkeletonUseCase:
    """为创作种子生成卷级骨架草稿。"""

    def __init__(
        self,
        repository: OutlineRepository,
        ai_port: OutlineAiPort,
        get_seed: GetSeedUseCase,
    ) -> None:
        """注入 repository、AI port 与 seed 查询用例。"""
        self._repository = repository
        self._ai_port = ai_port
        self._get_seed = get_seed

    def execute(self, seed_id: UUID) -> Skeleton:
        """生成并保存新的骨架草稿。

        AI adapter 返回的 volume 还没有 skeleton_id；保存前必须把新建 skeleton 的 ID
        回填到每个卷，否则持久化层无法建立骨架与卷的归属关系。
        """
        seed = self._get_seed.execute(seed_id)
        logger.info(
            "outline_skeleton_generation_started", extra={"seed_id": str(seed.id)}
        )
        volumes = self._ai_port.generate_skeleton(seed)
        logger.debug(
            "outline_skeleton_generation_ai_result_received",
            extra={"seed_id": str(seed.id), "volume_count": len(volumes)},
        )
        now = datetime.now(UTC)
        skeleton = Skeleton(
            seed_id=seed.id, volumes=volumes, created_at=now, updated_at=now
        )
        for volume in skeleton.volumes:
            # AI 只负责生成卷内容，归属关系与时间戳由业务侧统一补齐。
            volume.skeleton_id = skeleton.id
            volume.created_at = now
            volume.updated_at = now
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
