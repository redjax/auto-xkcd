from __future__ import annotations

import typing as t

import celery
from celery import Celery
from celery.result import AsyncResult
from celeryapp._celeryapp import app
from loguru import logger as log

@app.task
def demo_task_add(x, y):
    return x + y
