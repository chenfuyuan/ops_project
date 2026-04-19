import logging

from app.shared.infra.settings import AppSettings


def configure_logging(settings: AppSettings) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=f"%(asctime)s %(levelname)s [{settings.environment}] %(name)s - %(message)s",
    )
