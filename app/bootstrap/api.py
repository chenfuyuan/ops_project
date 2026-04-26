"""API 进程运行时装配入口。

这里集中选择 AI gateway、数据库 session 和 outline service 的具体实现，
避免接口层或业务层分散读取环境变量。
"""

import logging
import os

from app.bootstrap.ai_gateway import create_ai_gateway_facade
from app.bootstrap.novel_generate import create_outline_service
from app.bootstrap.settings import load_settings
from app.interfaces.http.app import build_http_app
from app.shared.infra.database import create_engine_from_settings, create_session_factory


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def create_api_app():
    """创建 API 进程的 FastAPI 应用，并集中完成运行时依赖装配。"""
    logger.info("api_app_composition_started")
    ai_gateway = create_ai_gateway_facade()
    outline_service = None
    database_configured = bool(os.environ.get("PERSON_UP_DATABASE_URL"))
    if database_configured:
        settings = load_settings()
        engine = create_engine_from_settings(settings)
        session_factory = create_session_factory(engine)
        outline_service = create_outline_service(ai_gateway, session_factory)
        logger.info(
            "api_outline_service_configured",
            extra={"database_configured": database_configured, "outline_enabled": True},
        )
    else:
        # 数据库未配置时仍注册 HTTP 路由，由占位 service 稳定返回 503。
        logger.warning(
            "api_outline_service_unavailable",
            extra={"database_configured": database_configured, "outline_enabled": False},
        )
    app = build_http_app(
        ai_gateway_checker=ai_gateway,
        outline_service=outline_service,
    )
    logger.info(
        "api_app_composition_completed",
        extra={"database_configured": database_configured, "outline_enabled": outline_service is not None},
    )
    return app
