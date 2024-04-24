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
    log.info(f"Retrieving Celery task {task_id}")

    log.debug(f"BACKEND URL: {celery_mod.celery_settings.backend_url}")
    try:
        # task_res: AsyncResult = celery_mod.celery_utils.check_task(task_id=task_id)
        task_res: AsyncResult = AsyncResult(f"{task_id}")

        res_dict = {
            "task": task_id,
            "state": task_res.state,
            # "ready": task_res.ready(),
            "status": task_res.status,
            "name": task_res.name,
            "date_done": task_res.date_done,
            "result": task_res.result,
            "errors": {"traceback": task_res.traceback},
        }

        return JSONResponse(status_code=status.HTTP_200_OK, content=res_dict)
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception checking task '{task_id}'. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "NotImplemented": f"Failed retrieving background task by id '{task_id}'."
            },
        )
