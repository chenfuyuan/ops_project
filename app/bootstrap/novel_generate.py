"""小说生成相关业务节点的运行时装配。"""

import logging

from sqlalchemy.orm import sessionmaker

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
from app.business.novel_generate.nodes.outline.facade import OutlineFacade
from app.business.novel_generate.nodes.outline.infrastructure.ai.outline_ai_adapter import (
    OutlineAiAdapter,
)
from app.business.novel_generate.nodes.outline.infrastructure.persistence.outline_repository import (
    OutlineRepositoryImpl,
)
from app.capabilities.ai_gateway import AiGatewayFacade

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def create_outline_service(
    ai_gateway: AiGatewayFacade,
    session_factory: sessionmaker,
) -> OutlineFacade:
    """装配 outline 节点运行时依赖，保持实现选择集中在 bootstrap。"""
    logger.info("outline_service_composition_started")
    repository = OutlineRepositoryImpl(session_factory)
    ai_port = OutlineAiAdapter(ai_gateway)
    get_seed = GetSeedUseCase(repository)
    facade = OutlineFacade(
        create_seed=CreateSeedUseCase(repository),
        get_seed=get_seed,
        generate_skeleton=GenerateSkeletonUseCase(repository, ai_port, get_seed),
        confirm_skeleton=ConfirmSkeletonUseCase(repository),
        expand_volume=ExpandVolumeUseCase(repository, ai_port, get_seed),
        update_volume=UpdateVolumeUseCase(repository),
        update_chapter=UpdateChapterUseCase(repository),
        get_outline=GetOutlineUseCase(repository, get_seed),
        repository=repository,
    )
    logger.info(
        "outline_service_composition_completed",
        extra={
            "repository_kind": type(repository).__name__,
            "ai_adapter_kind": type(ai_port).__name__,
        },
    )
    return facade
