from __future__ import annotations

from celery.result import AsyncResult
from loguru import logger as log


def check_task(task_id: str | None = None) -> AsyncResult:
    assert task_id, ValueError("Missing task_id to check.")

    try:
        task = AsyncResult(task_id)

        log.debug(f"Task ID [{task_id}] state: {task.state}")

        return task.state, task.result

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception checking task [{task_id}]. Details: {exc}"
        )
        log.error(msg)

        raise msg
