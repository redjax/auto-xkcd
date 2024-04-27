from __future__ import annotations

from functools import lru_cache
import typing as t

from .celery_tasks.scheduled import TASK_SCHEDULE_current_comic_check
import celery
from celery import Celery
from celery.schedules import crontab
from celery.result import AsyncResult
from celeryapp.celeryconfig import CelerySettings, celery_settings
from loguru import logger as log

app: Celery = Celery(
    "celery_tasks",
    broker=celery_settings.broker_url,
    backend=celery_settings.backend_url,
)
# app.autodiscover_tasks(
#     [
#         "celeryapp.celery_tasks.comic",
#         "celeryapp.celery_tasks.demo",
#     ]
# )

## Set app config
app.conf.update(timezone="America/New_York", enable_utc=True)


## Periodic jobs
@app.on_after_finalize.connect
def scheduled_tasks(sender, **kwargs):
    ## Call task_current_comic() every hour. Use imported schedule
    app.conf.beat_schedule = TASK_SCHEDULE_current_comic_check


log.debug(f"Discovered Celery tasks: {app.tasks}")


def check_task(task_id: str = None, app: Celery = app) -> AsyncResult | None:
    """Check a Celery task by its ID.

    Params:
        task_id (str): The Celery task's ID.
        app (Celery): An initialized Celery app.

    Returns:
        (AsyncResult): Returns a Celery `AsyncResult` object, if task is found.
        (None): If no task is found or an exception occurs.

    """
    assert task_id, ValueError("Missing a Celery task_id")
    task_id: str = f"{task_id}"

    log.info(f"Checking Celery task '{task_id}'")
    try:
        task_res: AsyncResult = app.AsyncResult(task_id)

        return task_res
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting task by ID '{task_id}'. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        return None
