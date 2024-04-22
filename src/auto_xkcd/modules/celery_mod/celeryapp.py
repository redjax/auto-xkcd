import typing as t

from core import paths
from .celery_config import celery_settings

from celery import Celery

# BROKER = celery_settings.broker_url
# BACKEND = celery_settings.backend_url

CELERY_APP: Celery = Celery(
    "auto_xkcd",
    broker=paths.CELERY_SQLITE_BROKER_URI,
    backend=paths.CELERY_SQLITE_BACKEND_URI,
    include=["modules.celery_mod.tasks"],
)

CELERY_APP.conf.update(result_expires=3600, result_max=10000)
