import typing as t

from core import paths
from .celery_config import celery_settings

from celery import Celery

BROKER = celery_settings.broker_url
BACKEND = celery_settings.backend_url

CELERY_APP: Celery = Celery(
    "auto_xkcd",
    broker=BROKER,
    backend=BACKEND,
    # include=["modules.celery_mod.tasks.comic_tasks"],
)

CELERY_APP.conf.update(result_expires=3600, result_max=10000)
