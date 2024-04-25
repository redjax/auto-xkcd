from __future__ import annotations

from pathlib import Path

from .methods import search_comic_img

from api import helpers as api_helpers
from api.api_responses import API_RESPONSES_DICT, img_response
from api.depends import cache_transport_dependency, db_dependency
from celery.result import AsyncResult
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

prefix: str = "/comics"
tags: list[str] = ["comic"]

router: APIRouter = APIRouter(prefix=prefix, responses=API_RESPONSES_DICT, tags=tags)

MAX_MULTI_SCRAPE: int = 10


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


@router.get("/by-num/{comic_num}")
def single_comic(comic_num: int) -> JSONResponse:
    try:
        comic_obj: comic.XKCDComic = xkcd_comic.comic.get_single_comic(
            comic_num=comic_num
        )

        res = JSONResponse(
            status_code=status.HTTP_200_OK, content=comic_obj.model_dump()
        )

        return res
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting XKCD comic #{comic_num}. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        exc_ts: str = time_utils.get_ts(as_str=True)

        res = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "InternalServerError": f"[{exc_ts}] Unhandled exception getting XKCD comic #{comic_num}. Check server logs"
            },
        )

        return res


@router.post("/multi")
def multiple_comics(comic_nums: list[int] = None) -> JSONResponse:
    if len(comic_nums) == 0 or comic_nums == [0]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "BadRequest": "comic_nums must be a list of 1 or more positive, non-zero integers."
            },
        )

    log.info(f"Starting multi-comic request chain")
    try:
        multi_comics_job: AsyncResult = xkcd_comic.comic.get_multiple_comics_task(
            comic_nums_lst=comic_nums
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"task_id": multi_comics_job.task_id},
        )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception requesting multiple XKCD comics. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "InternalServerError": f"Error while requesting [{len(comic_nums)}] XKCD comic(s)."
            },
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"NotImplemented": f"Would request XKCD comic numbers: {comic_nums}"},
    )

    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={
            "NotImplemented": "Requesting multiple XKCD comics at once is not yet implemented"
        },
    )


@router.get("/img/{comic_num}")
def comic_img(comic_num: int = None) -> JSONResponse:
    try:
        img_bytes: bytes = search_comic_img(comic_num=comic_num)
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception searching for XKCD comic #{comic_num} image. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "InternalServerError": f"Error retrieving image for XKCD comic #{comic_num}"
            },
        )

    if not img_bytes:
        not_found_str: str = (
            f"Did not find image for XKCD comic #{comic_num} locally, and failed retrieving from XKCD's API. Does that comic exist? https://xkcd.com/{comic_num}"
        )
        log.warning(not_found_str)

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"NotFound": not_found_str}
        )

    try:
        res: Response = img_response(img_bytes=img_bytes)

        return res
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting image bytestring for XKCD comic #{comic_num}. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "InternalServerError": f"Error preparing image Response for XKCD comic #{comic_num}"
            },
        )
