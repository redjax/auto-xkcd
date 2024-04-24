import typing as t

from core import paths
from .celery_config import celery_settings

from celery import Celery

from loguru import logger as log

BROKER = f"{celery_settings.broker_url}"
BACKEND = f"{celery_settings.backend_url}"

log.debug(f"Celery broker URL: {BROKER}")
log.debug(f"Celery backend URL: {BACKEND}")

CELERY_APP: Celery = Celery(
    "auto_xkcd",
    broker=BROKER,
    # backend=BACKEND,
    result_backend=BACKEND,
    include=["modules.celery_mod.tasks"],
)

CELERY_APP.conf.update(result_expires=3600, result_max=10000)
