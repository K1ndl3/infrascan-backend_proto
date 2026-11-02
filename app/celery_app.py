import os

from celery import Celery

celery_app = Celery(
    "infrascan",
    broker=os.environ.get("CELERY_BROKER_URL", "amqp://guest:guest@127.0.0.1:5672//"),
    backend=os.environ.get("CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/0"),
    include=["app.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    result_expires=3600,
    worker_prefetch_multiplier=1,
    task_acks_late=True
)
