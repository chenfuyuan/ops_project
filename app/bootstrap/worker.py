from celery import Celery

from app.bootstrap.settings import load_settings
from app.shared.infra.tasks import create_celery_app


app = create_celery_app(load_settings())


def create_worker_app() -> Celery:
    return app
