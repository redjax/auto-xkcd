import typing as t
from functools import lru_cache

from core.config import celery_settings, CelerySettings

import celery
from celery import Celery
from celery.result import AsyncResult

from loguru import logger as log

app: Celery = Celery(
    "tasks", broker=celery_settings.broker_url, backend=celery_settings.backend_url
)
