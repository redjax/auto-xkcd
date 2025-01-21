from __future__ import annotations

from . import celeryapp

from celery import Celery
from loguru import logger as log
from settings.celery_settings import CELERY_SETTINGS
from settings.logging_settings import LOGGING_SETTINGS
import setup

def start_celery_beat(app: Celery = celeryapp.app):
    """Starts the Celery beat schedule.
    
    Params:
        app (Celery): An initialized Celery app

    """
    log.debug(f"Celery app ({type(app)}): {app}")

    log.debug(f"Celery Beat schedule: {app.Beat().schedule}")
    log.info(f"Starting Celery Beat")
    try:
        app.Beat(loglevel=CELERY_SETTINGS.get("CELERY_LOG_LEVEL", default="INFO").lower()).run()
    except Exception as exc:
        msg = Exception(f"Unhandled exception starting Celery Beat. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc

if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"), colorize=True)
    setup.setup_database()

    start_celery_beat()
