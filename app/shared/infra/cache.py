from dataclasses import dataclass

from app.shared.infra.settings import AppSettings


@dataclass(frozen=True)
class CacheEndpoint:
    url: str


def create_cache_endpoint(settings: AppSettings) -> CacheEndpoint:
    return CacheEndpoint(url=settings.redis_url)
