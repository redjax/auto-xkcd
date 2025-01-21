from __future__ import annotations

from functools import lru_cache
import typing as t

from scheduling.celery_scheduler.celery_tasks.xkcd_api_tasks import (
    scheduled_tasks as celery_xkcd_api_scheduled_tasks,
)
from scheduling.celery_scheduler.celeryconfig import (
    CelerySettings,
    celery_settings,
    return_rabbitmq_url,
    return_redis_url,
)

## Import celery tasks
# from .celery_tasks import ...
import celery
from celery import Celery
from celery.result import AsyncResult
from celery.schedules import crontab
from loguru import logger as log
from settings.app_settings import APP_SETTINGS
from settings.celery_settings import CELERY_SETTINGS

# log.debug(f"Celery settings: {CELERY_SETTINGS.as_dict()}")

## Add paths Celery should look for tasks in
INCLUDE_TASK_PATHS: list[str] = [
    "scheduling.celery_scheduler.celery_tasks.xkcd_api_tasks.scheduled_tasks",
    "scheduling.celery_scheduler.celery_tasks.xkcd_api_tasks.tasks",
]

## List of scheduled task dicts to add to Celery beat's schedule
BEAT_SCHEDULED_TASKS: list = [
    ## Request & save current XKCD comic every hour
    celery_xkcd_api_scheduled_tasks.TASK_SCHEDULE_hourly_current_comic_check,
    ## Demo: request and save current XKCD comic every minute
    # celery_xkcd_api_scheduled_tasks.TASK_SCHEDULE_minutely_current_comic_check,
    ## Refresh current comic metadata in database every 5 minutes
    celery_xkcd_api_scheduled_tasks.TASK_SCHEDULE_5m_update_current_comic_metadata
]

app: Celery = Celery(
    "celery_tasks",
    # broker=celery_settings.broker_url,
    broker=return_rabbitmq_url(),
    # backend=celery_settings.backend_url,
    backend=return_redis_url(),
    include=INCLUDE_TASK_PATHS,
)

## Set app config
app.conf.update(timezone=APP_SETTINGS.get("TZ", default="Etc/UTC"), enable_utc=True)

## Autodiscover
app.autodiscover_tasks(INCLUDE_TASK_PATHS)


def print_discovered_tasks() -> list[str]:
    """Prints the list of discovered Celery tasks."""
    app.loader.import_default_modules()

    tasks: list[str] = list(
        sorted(name for name in app.tasks if not name.startswith("celery."))
    )

    print(f"Discovered [{len(tasks)}] Celery task(s): {[t for t in tasks]}")

    return tasks


## Periodic jobs
@app.on_after_finalize.connect
def scheduled_tasks(sender, **kwargs):
    """Configure the Celery beat schedule."""
    ## Call task_current_comic() every hour. Use imported schedule
    # app.conf.beat_schedule = <scheduled task name
    if not sender:
        ## This line is so vulture stops warning on unused variable 'sender'
        pass

    if not kwargs:
        ## This line is so vulture stops warning on unused variable 'kwargs'
        pass

    ## Configure celery beat schedule
    app.conf.beat_schedule = {
        task_name: task_config
        for task in BEAT_SCHEDULED_TASKS
        for task_name, task_config in task.items()
    }


# print_discovered_tasks()


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
