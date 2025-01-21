from __future__ import annotations

import typing as t

from celery import Celery
from celery.result import AsyncResult
from cyclopts import App, Group, Parameter
from domain import xkcd as xcd_domain

from scheduling.celery_scheduler.utils import get_celery_tasks_list, watch_celery_task, execute_celery_task

from loguru import logger as log
from scheduling.celery_scheduler import (
    CelerySettings,
    celery_settings,
    celeryapp,
    check_task,
    start_celery,
)

CELERY_APP: Celery = celeryapp.app

celery_app = App(name="celery", help="CLI for managing Celery scheduler.")

celery_tasks_app = App(name="tasks", help="CLI sub-app for Celery tasks")
tasks_call_app = App(name="call", help="Call specific Celery tasks by name")

celery_tasks_app.command(tasks_call_app)
celery_app.command(celery_tasks_app)


@celery_app.command(name="start")
def _start_celery(mode: t.Annotated[str, Parameter(name="mode", show_default=True, help="Set the mode Celery should run in, options: ['worker', 'beat']")]):
    """Start a Celery worker or beat schedule.
    
    Params:
        mode: The mode to run Celery in, options: ['worker', 'beat']
    """
    if not mode:
        log.error("Missing a --mode (-m). Please re-run with -m ['beat', 'worker'] (choose 1).")
        exit(1)
        
    if mode not in ["beat", "worker"]:
        raise ValueError(f"Invalid mode: {mode}. Must be one of ['beat', 'worker']")

    log.info(f"Starting Celery in '{mode}' mode.")
    
    try:
        start_celery.start(app=celeryapp.app, mode=mode)
    except Exception as exc:
        msg = f"({type(exc)}) Error running Celery in '{mode}' mode. Details: {exc}"
        log.error(msg)
        
        raise exc


@celery_tasks_app.command(name="list")
def list_celery_tasks(include_celery: t.Annotated[bool, Parameter(name="include-celery", help="When True, output will also show Celery tasks alongside discovered custom tasks.")] = False):
    tasks = get_celery_tasks_list(celery_app=celeryapp.app, include_celery_tasks=include_celery)
    
    print(f"[ Discovered Celery Tasks]")
    for t in tasks:
        print(f"- {t}")
    

@tasks_call_app.command(name="adhoc-current-comic")
def run_celery_current_comic_task(save: t.Annotated[bool, Parameter(name="save", help="When True, current comic & img will be saved to the database. When False, the current comic metadata will be returned.")]):
    if not save:
        celery_task: AsyncResult = execute_celery_task(task_name="current-comic", celery_app=CELERY_APP)
    else:
        # Save current comic metadata & image after running
        celery_task: AsyncResult = execute_celery_task(task_name="request_and_save_current_comic", celery_app=CELERY_APP)
        
    result = watch_celery_task(celery_task)
    print(f"Celery task 'adhoc-current-comic' result: {result[0]}")


@tasks_call_app.command(name="update-current-metadata")
def run_celery_update_current_comic_metadata_task():
    celery_task: AsyncResult = execute_celery_task(task_name="update_current_comic_metadata", celery_app=CELERY_APP)
    result = watch_celery_task(celery_task)
    
    print(f"Celery task 'update_current_comic_metadata' result: {result}")