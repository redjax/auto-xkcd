from __future__ import annotations

from celery import Celery
from loguru import logger as log
from packages import celeryapp
from setup import base_app_setup

if __name__ == "__main__":
    base_app_setup()

    log.debug(f"Celery app ({type(celeryapp.app)}): {celeryapp.app}")

    celeryapp.app.autodiscover_tasks(["packages.celery_app"])

    try:
        worker = celeryapp.app.worker_main(
            argv=["worker", "--loglevel=DEBUG", "--uid=0", "--gid=0"]
        )
    except Exception as exc:
        msg = Exception(f"Unhandled exception getting Celery worker. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc

    log.info("Starting Celery worker")
    try:
        worker.start()
    except Exception as exc:
        msg = Exception(f"Unhandled exception starting Celery worker. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc
