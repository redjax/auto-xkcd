from packages import celery_app
from celery import Celery


from setup import base_app_setup
from loguru import logger as log

if __name__ == "__main__":
    base_app_setup()

    log.debug(f"Celery app ({type(celery_app.app)}): {celery_app.app}")

    celery_app.app.autodiscover_tasks(["packages.celery_app"])

    try:
        worker = celery_app.app.worker_main(
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
