from dataclasses import dataclass

from app.shared.infra.logger import configure_logging
from app.shared.infra.settings import AppSettings, load_settings


@dataclass(slots=True)
class AppContainer:
    settings: AppSettings


def build_container() -> AppContainer:
    settings = load_settings()
    configure_logging(settings)
    return AppContainer(settings=settings)
