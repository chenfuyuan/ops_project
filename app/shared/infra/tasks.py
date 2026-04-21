from celery import Celery

from app.shared.infra.settings import AppSettings


def create_celery_app(settings: AppSettings) -> Celery:
    app = Celery("person_up_ops_project.worker")
    app.conf.broker_url = settings.celery_broker_url
    app.conf.result_backend = settings.celery_result_backend
    return app
