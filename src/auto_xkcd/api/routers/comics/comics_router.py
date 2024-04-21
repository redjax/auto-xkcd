import typing as t
import sqlite3 as sqlite

from api.responses import API_RESPONSES_DICT
from api.depends import cache_transport_dependency, db_dependency
from core import request_client
from domain.xkcd import comic
from packages import xkcd_comic
from modules import data_mod, xkcd_mod, msg_mod
from core.config import settings, db_settings

from loguru import logger as log
from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from red_utils.ext import time_utils

import hishel

prefix: str = "/comics"
tags: list[str] = ["comic"]

router: APIRouter = APIRouter(prefix=prefix, responses=API_RESPONSES_DICT)


@router.get("/current")
def current_comic() -> JSONResponse:
    try:
        comic_obj: comic.XKCDComic = xkcd_comic.current_comic.get_current_comic()
        res = JSONResponse(
            status_code=status.HTTP_200_OK, content=comic_obj.model_dump()
        )
    except Exception as exc:
        msg = Exception(f"Unhandled exception getting current comic. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        exc_ts: str = time_utils.get_ts(as_str=True)

        res = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "InternalServerError": f"[{exc_ts}] Unhandled exception getting current XKCD comic. Check server logs."
            },
        )

    return res
