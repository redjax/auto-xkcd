from loguru import logger as log
from celery.result import AsyncResult
from celery import Celery

from .xkcd_api_tasks import tasks as xkcd_api_tasks, scheduled_tasks as xkcd_api_scheduled_tasks, adhoc_tasks as xkcd_api_adhoc_tasks

from scheduling.celery_scheduler import celeryapp, check_task


def execute_celery_task(task_name: str) -> dict | None:
    if not task_name:
        raise  ValueError("Missing task_name, which should be the name of a celery task.")
    
    log.debug(f"Attempting to execute Celery task: {task_name}")
    
    
def get_celery_tasks_list(celery_app: Celery = celeryapp.app, hide_celery_tasks: bool = True) -> list[str] | None:
    """Return list of Celery tasks your app is aware of."""
    try:
        if hide_celery_tasks:
            celery_tasks: list[str] = [name for name in celery_app.tasks.keys() if not name.startswith('celery.')]
        else:
            celery_tasks: list[str] = [name for name in celery_app.tasks.keys()]

        return celery_tasks
    except Exception as exc:
        msg = f"({type(exc)}) Error listing Celery tasks. Details: {exc}"
        log.error(msg)
        
        return []
