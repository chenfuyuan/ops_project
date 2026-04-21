from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite+pysqlite:///:memory:"
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    object_storage_endpoint_url: str = "http://localhost:9000"
    object_storage_bucket: str = "person-up"

    model_config = SettingsConfigDict(env_prefix="PERSON_UP_", extra="ignore")
