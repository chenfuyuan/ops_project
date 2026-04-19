import os
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class AppSettings:
    service_name: str = "ops-project"
    environment: str = "development"


def load_settings() -> AppSettings:
    return AppSettings(
        service_name=os.getenv("APP_NAME", "ops-project"),
        environment=os.getenv("APP_ENV", "development"),
    )
