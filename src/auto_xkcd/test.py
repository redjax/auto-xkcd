from modules import celery_mod
from loguru import logger as log
from setup import base_app_setup
from modules.celery_mod.tasks import comic_tasks

if __name__ == "__main__":
    base_app_setup()
    log.info("CELERY TEST")

    log.debug(f"Celery settings: {celery_mod.celery_settings}")

    # current_comic_task = comic_tasks.task_current_comic().delay(2, 3)
    # log.debug(f"Current comic task: {current_comic_task}")

    app = celery_mod.CELERY_APP
    log.debug(f"App ({type(app)}): {app}")
    try:
        app.start()
    except Exception as exc:
        msg = Exception(f"Unhandled exception starting Celery app. Details: {exc}")
        log.error(msg)
