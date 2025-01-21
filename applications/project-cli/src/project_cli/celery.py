from __future__ import annotations

import typing as t

from celery import Celery
from cyclopts import App, Group, Parameter
from domain import xkcd as xcd_domain

from loguru import logger as log
from scheduling.celery_scheduler import (
    CelerySettings,
    celery_settings,
    celeryapp,
    check_task,
    start_celery,
)

celery_app = App(name="celery", help="CLI for managing Celery scheduler.")


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
