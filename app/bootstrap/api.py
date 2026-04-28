"""API 进程运行时装配入口。

这里集中选择 AI gateway 的具体实现，
避免接口层或业务层分散读取环境变量。
"""

import logging

from app.bootstrap.ai_gateway import create_ai_gateway_facade
from app.interfaces.http.app import build_http_app


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def create_api_app():
    """创建 API 进程的 FastAPI 应用，并集中完成运行时依赖装配。"""
    logger.info("api_app_composition_started")
    ai_gateway = create_ai_gateway_facade()
    app = build_http_app(
        ai_gateway_checker=ai_gateway,
    )
    logger.info("api_app_composition_completed")
    return app
