import typing as t
from functools import lru_cache

from core.config import celery_settings, CelerySettings

import celery
from celery import Celery

celery_app: Celery = Celery(
    "tasks", broker=celery_settings.broker_url, backend=celery_settings.backend_url
)


@celery_app.task
def task_add(x, y):
    return x + y
