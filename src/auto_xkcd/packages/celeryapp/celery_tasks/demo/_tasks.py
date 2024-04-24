import typing as t

from modules.celery_mod import app
import celery
from celery import Celery
from celery.result import AsyncResult

from loguru import logger as log


@app.task
def demo_task_add(x, y):
    return x + y
