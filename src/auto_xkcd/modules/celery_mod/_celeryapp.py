from __future__ import annotations

from functools import lru_cache
import typing as t

import celery
from celery import Celery
from celery.result import AsyncResult
from core.config import CelerySettings, celery_settings
from loguru import logger as log

app: Celery = Celery(
    "tasks", broker=celery_settings.broker_url, backend=celery_settings.backend_url
)
