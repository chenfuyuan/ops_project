from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from app.shared.infra.settings import AppSettings


def create_engine_from_settings(settings: AppSettings) -> Engine:
    return create_engine(settings.database_url)


def create_session_factory(engine: Engine) -> sessionmaker:
    return sessionmaker(bind=engine)
