from __future__ import annotations

import typing as t

import celery
from celery import Celery
from celery.result import AsyncResult
from loguru import logger as log
from modules.celery_mod import app

@app.task
def demo_task_add(x, y):
    return x + y
