from app.shared.infra.settings import AppSettings


def load_settings() -> AppSettings:
    return AppSettings()
