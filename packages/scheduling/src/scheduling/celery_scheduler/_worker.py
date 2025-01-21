from __future__ import annotations

import subprocess

from . import celeryapp

from celery import Celery
from loguru import logger as log
from settings.celery_settings import CELERY_SETTINGS
from settings.logging_settings import LOGGING_SETTINGS
import setup

def start_celery_worker(app: Celery = celeryapp.app):
    """Starts the Celery worker.
    
    Params:
        app (Celery): An initialized Celery app

    """
    log.debug(f"Celery app ({type(app)}): {app}")

    app.autodiscover_tasks(
        packages=[
            "scheduling.celery_scheduler.celery_tasks.weatherapi_tasks"
        ]
    )

    log.info("Starting Celery worker")
    try:
        app.worker_main(
            argv=["worker", "--loglevel=DEBUG", "--uid=0", "--gid=0"]
        )
    except Exception as exc:
        msg = Exception(f"Unhandled exception getting Celery worker. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"), colorize=True)
    setup.setup_database()

    start_celery_worker()
