import typing as t
import time

from celery.result import AsyncResult

from core.dependencies import get_db
from core import request_client
from modules.celery_mod.celery_utils import check_task
from modules.celery_mod.celeryapp import CELERY_APP
from modules.celery_mod.celery_config import celery_settings
from modules.celery_mod.tasks import comic_tasks

from loguru import logger as log


def current_comic():
    current_comic_task = comic_tasks.task_current_comic()
    log.debug(f"CURRENT COMIC CELERY TASK ({type(current_comic_task)})")
