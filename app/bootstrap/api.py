from app.bootstrap.ai_gateway import create_ai_gateway_facade
from app.interfaces.http.app import build_http_app


def create_api_app():
    """创建 API 进程的 FastAPI 应用，并集中完成运行时依赖装配。"""
    ai_gateway = create_ai_gateway_facade()
    return build_http_app(ai_gateway_checker=ai_gateway)
