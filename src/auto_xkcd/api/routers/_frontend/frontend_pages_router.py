from __future__ import annotations

import base64
from pathlib import Path
import random
import time
import typing as t

from .methods import get_templates_dir

from api import helpers as api_helpers
from api.depends import cache_transport_dependency, db_dependency

# from api.api_responses import API_RESPONSES_DICT, img_response
from api.routers._frontend._responses import FRONTEND_RESPONSES_DICT

# from celery.result import AsyncResult
# import celeryapp
from core import request_client
from core.config import db_settings, settings
from core.constants import IGNORE_COMIC_NUMS, XKCD_URL_BASE, XKCD_URL_POSTFIX
from domain.xkcd import comic
from fastapi import APIRouter, Depends, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    Response,
    StreamingResponse,
)
from fastapi.templating import Jinja2Templates
from helpers import data_ctl
import hishel
from loguru import logger as log
from modules import data_mod, msg_mod, xkcd_mod
from packages import xkcd_comic
from red_utils.ext import time_utils

templates: Jinja2Templates = get_templates_dir(templates_dirname="auto_xkcd/templates")

prefix: str = ""
tags: list[str] = ["frontend"]

router: APIRouter = APIRouter(
    responses=FRONTEND_RESPONSES_DICT, prefix=prefix, tags=tags
)


@router.get("/", response_class=HTMLResponse)
def render_home_page(request: Request) -> HTMLResponse:
    template = templates.TemplateResponse(
        request=request,
        name="pages/index.html",
        status_code=status.HTTP_200_OK,
        context={"page_title": "home"},
    )

    return template


@router.get("/comics", response_class=HTMLResponse)
def render_comics_page(request: Request) -> HTMLResponse:
    template = templates.TemplateResponse(
        request=request,
        name="pages/comics.html",
        status_code=status.HTTP_200_OK,
        context={"page_title": "comics"},
    )

    return template


@router.get("/comics/all", response_class=HTMLResponse)
def render_all_comics_page(request: Request) -> HTMLResponse:
    count_comics = xkcd_mod.count_comics_in_db()
    template = templates.TemplateResponse(
        request=request,
        name="pages/comics_all.html",
        status_code=status.HTTP_200_OK,
        context={"page_title": "all comics", "count": count_comics},
    )

    return template


@router.get("/comics/random", response_class=HTMLResponse)
def render_random_comics_page(request: Request) -> HTMLResponse:
    ## Load current XKCD comic metadata from file to set max number for random comic
    try:
        current_comic_metadata = xkcd_comic.current_comic.get_current_comic_metadata()
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception loading current XKCD comic metadata from file, and failed requesting current comic. Details: {exc}"
        )
        log.error(msg)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "InternalServerError": "Error loading random XKCD comic. Check the server logs."
            },
        )

    current_comic_num: int = current_comic_metadata.comic_num

    ## Get a random comic number betwee 1 and the current XKCD comic number
    rand_index: int = random.randint(1, current_comic_num)

    ## Re-roll if rand_index is 404
    while rand_index in IGNORE_COMIC_NUMS:
        log.warning(
            f"Random comic number [{rand_index}] is in ignored list. Re-rolling"
        )
        rand_index = random.randint(1, current_comic_num)

    ## Load/request comic
    _comic: comic.XKCDComic | None = xkcd_comic.comic.get_single_comic(
        comic_num=rand_index
    )

    if _comic is None:
        ## Comic not found, checked DB, serialized files, and attempted a live request.
        log.warning(f"Comic #{rand_index} not found.")

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "NotFound": f"Could not find XKCD comic #{rand_index} locally, and failed requesting from the XKCD API."
            },
        )

    log.debug(f"COMIC ({type(_comic)}):\n{_comic}")

    try:
        ## Load comic image from database
        _comic_img: comic.XKCDComicImage | None = (
            xkcd_comic.comic_img.retrieve_img_from_db(comic_num=rand_index)
        )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception loading XKCD comic #{rand_index} image from database. Details: {exc}"
        )
        log.error(msg)

    if _comic_img is None:
        ## Comic not found in database, request from API and save
        log.warning(f"Comic #{rand_index} image not found.")

        _comic_img = xkcd_mod.save_comic_img(comic_obj=_comic)

    ## Encode img bytes so comic image can be rendered on webpage
    try:
        img_base64 = xkcd_mod.encode_img_bytes(_comic_img.img)
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception converting XKCD comic #{rand_index} image to base64-encoded bytes. Details: {exc}"
        )
        log.error(msg)

    ## Build template response
    template = templates.TemplateResponse(
        request=request,
        name="pages/comics_random.html",
        status_code=status.HTTP_200_OK,
        context={
            "page_title": "random comic",
            "comic": _comic,
            "comic_img": img_base64,
        },
    )

    return template


## Keep at bottom to avoid overriding other URLs
@router.get("/comics/{comic_num}", response_class=HTMLResponse)
def render_single_comic_page(request: Request, comic_num: int) -> HTMLResponse:
    ## Load/request comic
    _comic: comic.XKCDComic | None = xkcd_comic.comic.get_single_comic(
        comic_num=comic_num
    )

    if _comic is None:
        ## Comic not found, checked DB, serialized files, and attempted a live request.
        log.warning(f"Comic #{comic_num} not found.")

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "NotFound": f"Could not find XKCD comic #{comic_num} locally, and failed requesting from the XKCD API."
            },
        )

    log.debug(f"COMIC ({type(_comic)}):\n{_comic}")

    try:
        ## Load comic image from database
        _comic_img: comic.XKCDComicImage | None = (
            xkcd_comic.comic_img.retrieve_img_from_db(comic_num=comic_num)
        )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception loading XKCD comic #{comic_num} image from database. Details: {exc}"
        )
        log.error(msg)

    if _comic_img is None:
        ## Comic not found in database, request from API and save
        log.warning(f"Comic #{comic_num} image not found.")

        _comic_img = xkcd_mod.save_comic_img(comic_obj=_comic)

    ## Encode img bytes so comic image can be rendered on webpage
    try:
        img_base64 = xkcd_mod.encode_img_bytes(_comic_img.img)
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception converting XKCD comic #{comic_num} image to base64-encoded bytes. Details: {exc}"
        )
        log.error(msg)

    ## Build template response
    template = templates.TemplateResponse(
        request=request,
        name="pages/comics_random.html",
        status_code=status.HTTP_200_OK,
        context={
            "page_title": f"#{_comic.comic_num}",
            "comic": _comic,
            "comic_img": img_base64,
        },
    )

    return template
