import sqlite3 as sqlite
import typing as t
from pathlib import Path

from api.depends import cache_transport_dependency, db_dependency
from api.api_responses import API_RESPONSES_DICT, img_response
from api import helpers as api_helpers

from core import request_client
from core.config import db_settings, settings
from core.constants import XKCD_URL_BASE, XKCD_URL_POSTFIX
from domain.xkcd import comic

from fastapi import APIRouter, Depends, status, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response, StreamingResponse, FileResponse
import hishel
from loguru import logger as log
from modules import data_mod, msg_mod, xkcd_mod, celery_mod
from packages import xkcd_comic
from red_utils.ext import time_utils
from celery.result import AsyncResult

prefix: str = "/test"
tags: list[str] = ["test"]

router: APIRouter = APIRouter(prefix=prefix, responses=API_RESPONSES_DICT, tags=tags)


@router.get("/")
def testing_root() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"msg": "testing root reached"}
    )


@router.get("/trigger-new-comic")
def test_route() -> JSONResponse:
    log.info("Starting background task")
    try:
        task: AsyncResult = celery_mod.tasks.comic_tasks.task_current_comic.delay()
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception running background task to get current comic. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Background task exited unexpectedly."},
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"success": True, "task_id": task.id}
    )