from __future__ import annotations

from celery import Celery
import celeryapp
from core.config import settings
from loguru import logger as log
from setup import base_app_setup

if __name__ == "__main__":
    base_app_setup()

    log.debug(f"Celery app ({type(celeryapp.app)}): {celeryapp.app}")

    log.debug(f"Celery Beat schedule: {celeryapp.app.Beat().schedule}")
    try:
        log.info(f"Starting Celery Beat")
        celeryapp.app.Beat(loglevel=settings.log_level.lower()).run()
    except Exception as exc:
        msg = Exception(f"Unhandled exception starting Celery Beat. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc
