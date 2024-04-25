from __future__ import annotations

from pathlib import Path
import typing as t

from api import helpers as api_helpers
from api.api_responses import API_RESPONSES_DICT, img_response
from api.depends import cache_transport_dependency, db_dependency
from celery.result import AsyncResult
import celeryapp
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

prefix: str = "/tasks"
tags: list[str] = ["task"]

router: APIRouter = APIRouter(prefix=prefix, responses=API_RESPONSES_DICT, tags=tags)


@router.get("/")
def tasks_root() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"msg": "Tasks root reached"}
    )


@router.get("/id/{task_id}")
def task_by_id(task_id: str) -> JSONResponse:
    log.info(f"Checking background task '{task_id}'")

    try:
        res: AsyncResult = celeryapp.check_task(task_id=task_id)
        log.debug(
            f"Task '{task_id}':\n\tReady: {res.ready()}\n\tState: {res.state}\n\tStatus: {res.status}"
        )

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting task '{task_id}' results. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "NotImplemented": f"Failed retrieving background task by id '{task_id}'."
            },
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
