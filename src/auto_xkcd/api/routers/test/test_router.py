from __future__ import annotations

from pathlib import Path
import sqlite3 as sqlite
import typing as t

from api import helpers as api_helpers
from api.api_responses import API_RESPONSES_DICT, img_response
from api.depends import cache_transport_dependency, db_dependency
from celery.result import AsyncResult
from celeryapp import (
    app as celery_app,
    celery_tasks,
    check_task,
)
from core import request_client
from core.config import db_settings, settings
from core.constants import XKCD_URL_BASE, XKCD_URL_POSTFIX
from domain.xkcd import comic
from fastapi import APIRouter, Depends, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
import hishel
from loguru import logger as log
from modules import data_mod, msg_mod, xkcd_mod
from packages import xkcd_comic
from red_utils.ext import time_utils

prefix: str = "/test"
tags: list[str] = ["test"]

router: APIRouter = APIRouter(prefix=prefix, responses=API_RESPONSES_DICT, tags=tags)


@router.get("/")
def testing_root() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"msg": "testing root reached"}
    )


# @router.get("/trigger-new-comic")
# def test_route() -> JSONResponse:
#     log.info("Starting background task")
#     try:
#         task: AsyncResult = celery_mod.tasks.comic_tasks.task_current_comic.delay()
#     except Exception as exc:
#         msg = Exception(
#             f"Unhandled exception running background task to get current comic. Details: {exc}"
#         )
#         log.error(msg)
#         log.trace(exc)

#         return JSONResponse(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             content={"error": "Background task exited unexpectedly."},
#         )

#     return JSONResponse(
#         status_code=status.HTTP_200_OK, content={"success": True, "task_id": task.id}
#     )


@router.get("/add-nums-task")
def test_add_nums(x: int, y: int) -> JSONResponse:
    result = celery_tasks.demo.demo_task_add.delay(4, 4)

    print(f"Ready: {result.ready()}")

    print(f"GET result: {result.get(timeout=1)}")

    return JSONResponse(status_code=status.HTTP_200_OK, content={"task_id": result.id})


@router.get("/check-task")
def check_task_by_id(task_id: str) -> JSONResponse:
    # res: AsyncResult = celery_app.app.AsyncResult(f"{task_id}")
    res: AsyncResult = check_task(task_id=task_id)

    log.debug(f"Task res ({res}): {res}")

    log.debug(
        f"Task '{task_id}':\n\tReady: {res.ready()}\n\tState: {res.state}\n\tStatus: {res.status}"
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "task_id": task_id,
            "ready": res.ready(),
            "state": res.state,
            "results": res.result,
        },
    )
