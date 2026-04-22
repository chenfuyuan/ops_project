from app.bootstrap.worker import create_worker_app


worker_app = create_worker_app()
app = worker_app
