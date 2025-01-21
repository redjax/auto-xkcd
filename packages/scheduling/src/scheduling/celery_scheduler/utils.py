from loguru import logger as log
from celery.result import AsyncResult
from celery import Celery
import typing as t


def execute_celery_task(task_name: str, celery_app: Celery, *args, **kwargs) -> AsyncResult:
    """Execute a Celery task by its name, passing optional arguments.

    Params:
        task_name (str): The name of the Celery task to execute.
        *args: Positional arguments to pass to the task.
        **kwargs: Keyword arguments to pass to the task.

    Returns:
        (AsyncResult): The Celery async result object for the task.

    Raises:
        ValueError: If task_name is not provided.
        Exception: If there is an error executing the task.

    """
    if not task_name:
        raise ValueError("Missing task_name, which should be the name of a Celery task.")
    if not celery_app:
        raise ValueError("Missing a Celery app to send task to.")
    
    log.info(f"Attempting to execute Celery task: {task_name} with args: {args} and kwargs: {kwargs}")
    
    try:
        # Send the task
        async_res: AsyncResult = celery_app.send_task(task_name, args=args, kwargs=kwargs)
        
        log.info(f"Task {task_name} submitted with ID: {async_res.id}")
        return async_res
    except Exception as exc:
        msg = f"({type(exc)}) Error executing Celery task '{task_name}'. Details: {exc}"
        log.error(msg)
        raise exc


def watch_celery_task(async_res: AsyncResult, timeout: int = 30) -> t.Any:
    """Monitor and retrieve the result of a Celery task.

    Params:
        async_res (AsyncResult): The Celery async result object.
        timeout (int): Maximum time (in seconds) to wait for the task result. Defaults to 30.

    Returns:
        (Any): The result of the task.

    Raises:
        TimeoutError: If the task does not complete within the timeout period.
        Exception: If there is an error retrieving the result.

    """
    try:
        log.info(f"Waiting for task {async_res.id} to complete...")
        result = async_res.get(timeout=timeout)
        log.info(f"Task {async_res.id} completed with result.")
        return result
    except TimeoutError:
        log.warning(f"Task {async_res.id} did not complete within {timeout} seconds.")
        raise
    except Exception as exc:
        msg = f"({type(exc)}) Error retrieving result for task {async_res.id}. Details: {exc}"
        log.error(msg)
        raise

    
def get_celery_tasks_list(celery_app: Celery, include_celery_tasks: bool = False) -> list[str] | None:
    """Return list of Celery tasks your app is aware of."""
    if not celery_app:
        raise ValueError("Missing a celery_app to get tasks from.")

    try:
        if include_celery_tasks:
            celery_tasks: list[str] = [name for name in celery_app.tasks.keys()]
        else:
            celery_tasks: list[str] = [name for name in celery_app.tasks.keys() if not name.startswith('celery.')]

        return celery_tasks
    except Exception as exc:
        msg = f"({type(exc)}) Error listing Celery tasks. Details: {exc}"
        log.error(msg)
        
        return []
