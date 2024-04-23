from setup import base_app_setup
from modules import celery_mod
from loguru import logger as log

if __name__ == "__main__":
    base_app_setup()

    try:
        celery_mod.CELERY_APP.start()
    except Exception as exc:
        msg = Exception(f"Unhandled exception starting Celery app. Details: {exc}")
        log.error(msg)
