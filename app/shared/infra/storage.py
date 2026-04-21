from dataclasses import dataclass

from app.shared.infra.settings import AppSettings


@dataclass(frozen=True)
class ObjectStorageEndpoint:
    endpoint_url: str
    bucket: str


def create_object_storage_endpoint(settings: AppSettings) -> ObjectStorageEndpoint:
    return ObjectStorageEndpoint(
        endpoint_url=settings.object_storage_endpoint_url,
        bucket=settings.object_storage_bucket,
    )
