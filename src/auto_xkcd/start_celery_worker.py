from __future__ import annotations

from celery import Celery
import celeryapp
from loguru import logger as log
from setup import base_app_setup

if __name__ == "__main__":
    base_app_setup()

    log.debug(f"Celery app ({type(celeryapp.app)}): {celeryapp.app}")

    # celeryapp.app.autodiscover_tasks(["celeryapp.celery_tasks"])
    celeryapp.app.autodiscover_tasks(
        packages=[
            "celeryapp.celery_tasks.comic",
            "celeryapp.celery_tasks.demo",
        ]
    )

    try:
        worker = celeryapp.app.worker_main(
            argv=["worker", "--loglevel=DEBUG", "--uid=1000", "--gid=1000"]
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
