"""小说生成相关业务节点的运行时装配。"""

import logging

from sqlalchemy.orm import sessionmaker

from app.business.novel_generate.nodes.outline.infrastructure.ai_adapter import OutlineAiAdapter
from app.business.novel_generate.nodes.outline.infrastructure.repository import OutlineRepositoryImpl
from app.business.novel_generate.nodes.outline.service import OutlineNodeService
from app.capabilities.ai_gateway import AiGatewayFacade


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def create_outline_service(
    ai_gateway: AiGatewayFacade,
    session_factory: sessionmaker,
) -> OutlineNodeService:
    """装配 outline 节点运行时依赖，保持实现选择集中在 bootstrap。"""
    logger.info("outline_service_composition_started")
    repository = OutlineRepositoryImpl(session_factory)
    ai_port = OutlineAiAdapter(ai_gateway)
    service = OutlineNodeService(repository, ai_port)
    logger.info(
        "outline_service_composition_completed",
        extra={
            "repository_kind": type(repository).__name__,
            "ai_adapter_kind": type(ai_port).__name__,
        },
    )
    return service
