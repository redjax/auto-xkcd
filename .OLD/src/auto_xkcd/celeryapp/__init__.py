# from .methods import current_comic
from __future__ import annotations

from . import celery_tasks
from ._celeryapp import app, check_task
from .celeryconfig import CelerySettings, celery_settings
