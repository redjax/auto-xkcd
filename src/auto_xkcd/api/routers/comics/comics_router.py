from __future__ import annotations

import sqlite3 as sqlite
import typing as t
from pathlib import Path

from api.depends import cache_transport_dependency, db_dependency
from api.responses import API_RESPONSES_DICT
from api import helpers as api_helpers

from core import request_client
from core.config import db_settings, settings
from domain.xkcd import comic
from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response, StreamingResponse, FileResponse
import hishel
from loguru import logger as log
from modules import data_mod, msg_mod, xkcd_mod
from packages import xkcd_comic
from red_utils.ext import time_utils

prefix: str = "/comics"
tags: list[str] = ["comic"]

router: APIRouter = APIRouter(prefix=prefix, responses=API_RESPONSES_DICT)

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


@router.get("/{comic_num}")
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
    if len(comic_nums) > MAX_MULTI_SCRAPE:
        log.error(f"Exceeded MAX_MULTI_SCRAPE: [{len(comic_nums)}/{MAX_MULTI_SCRAPE}]")

        res: JSONResponse = JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "MalformedRequest": f"Exceeded maximum number of comic numbers to request at once. List of comic_nums must be less than {MAX_MULTI_SCRAPE}"
            },
        )

        return res

    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={
            "NotImplemented": "Requesting multiple XKCD comics at once is not yet implemented"
        },
    )


@router.get("/img/{comic_num}")
def comic_img(comic_num: int = None) -> JSONResponse:
    def search_for_img_file() -> Path | None:
        ## Get image file
        try:
            img_file: Path | None = xkcd_mod.lookup_img_file(comic_num=comic_num)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception getting image for XKCD comic #{comic_num}. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            raise exc

        return img_file

        # res: JSONResponse = JSONResponse(
        #     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #     content={
        #         "InternalServerError": f"Unhandled error while retrieving image for XKCD comic #{comic_num}"
        #     },
        # )

        # return res

    ## Get image file
    try:
        # img_file: Path | None = xkcd_mod.lookup_img_file(comic_num=comic_num)
        img_file: Path | None = search_for_img_file()
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting image for XKCD comic #{comic_num}. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        # res: JSONResponse = JSONResponse(
        #     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #     content={
        #         "InternalServerError": f"Unhandled error while retrieving image for XKCD comic #{comic_num}"
        #     },
        # )

        # return res

    ## Image file not found
    if img_file is None:
        # res: JSONResponse = JSONResponse(
        #     status_code=status.HTTP_404_NOT_FOUND,
        #     content={
        #         "FileNotFound": f"Could not find image file for XKCD comic #{comic_num}"
        #     },
        # )

        # return res

        log.warning(f"Image not found for XKCD comic #{comic_num}.")

        log.info(f"Requesting XKCD comic #{comic_num}, then returning image.")
        try:
            ## Request the missing comic image
            comic_obj: comic.XKCDComic = xkcd_comic.comic.get_single_comic(
                comic_num=comic_num
            )
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception getting XKCD comic #{comic_num}. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            res: JSONResponse = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "InternalServerError": f"Image was not found for XKCD comic #{comic_num}, and an error occurred while downloading it from the XKCD API."
                },
            )

            return res

        ## Retry getting img file after requesting
        try:
            # img_file: Path | None = xkcd_mod.lookup_img_file(comic_num=comic_num)
            img_file: Path | None = search_for_img_file()
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception getting image for XKCD comic #{comic_num}. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            ## Return error response after second attempt
            res: JSONResponse = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "InternalServerError": f"Unhandled error while retrieving image for XKCD comic #{comic_num}"
                },
            )

            return res

    log.info(
        f"Found image file for XKCD comic #{comic_num} at path '{img_file}'. Streaming file response..."
    )
    try:
        return StreamingResponse(
            content=api_helpers.response_helpers.stream_file_contents(f_path=img_file),
            media_type="image/png",
        )
    except Exception as exc:
        res: JSONResponse = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "InternalServerError": f"Unhandled error streaming image for XKCD comic #{comic_num}"
            },
        )

        return res
