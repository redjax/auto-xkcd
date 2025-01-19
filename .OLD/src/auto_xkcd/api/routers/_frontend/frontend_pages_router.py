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
from core import request_client, paths
from core.config import db_settings, settings
from core.constants import IGNORE_COMIC_NUMS, XKCD_URL_BASE, XKCD_URL_POSTFIX
from core.dependencies import get_db
from domain.xkcd import comic
from domain.api.api_responses.frontend_responses import DirSizeResponse
from utils.path_utils import get_dir_size

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

if settings.container_env:
    templates_str = "auto_xkcd/templates"
else:
    templates_str: str = "src/auto_xkcd/templates"

templates: Jinja2Templates = get_templates_dir(templates_dirname=templates_str)

prefix: str = ""
tags: list[str] = ["frontend"]

router: APIRouter = APIRouter(
    responses=FRONTEND_RESPONSES_DICT, prefix=prefix, tags=tags
)


def is_current(comic_num: int = None) -> bool:
    current_comic_meta = xkcd_comic.current_comic.get_current_comic_metadata()

    if comic_num == current_comic_meta.comic_num:
        return True
    else:
        return False


@router.get("/error")
def render_error_page(request: Request):
    ## Build template response
    template = templates.TemplateResponse(
        request=request,
        name="pages/error/default_404.html",
        status_code=status.HTTP_404_NOT_FOUND,
        context={
            "page_title": "NotFound",
        },
    )

    return template


@router.get("/", response_class=HTMLResponse)
def render_home_page(request: Request) -> HTMLResponse:
    try:
        current_comic = xkcd_comic.current_comic.get_current_comic()
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting current XKCD comic for home page. Details: {exc}"
        )
        log.error(msg)

        current_comic = None

    try:
        ## Load comic image from database
        comic_img: comic.XKCDComicImage | None = (
            xkcd_comic.comic_img.retrieve_img_from_db(comic_num=current_comic.comic_num)
        )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception loading XKCD comic #{current_comic.comic_num} image from database. Details: {exc}"
        )
        log.error(msg)

    if comic_img is None:
        ## Comic not found in database, request from API and save
        log.warning(f"Comic #{current_comic.comic_num} image not found.")

        comic_img = xkcd_mod.save_comic_img(comic_obj=current_comic.comic_num)

    ## Encode img bytes so comic image can be rendered on webpage
    try:
        img_base64 = xkcd_mod.encode_img_bytes(comic_img.img)
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception converting XKCD comic #{current_comic.comic_num} image to base64-encoded bytes. Details: {exc}"
        )
        log.error(msg)

    template = templates.TemplateResponse(
        request=request,
        name="pages/index.html",
        status_code=status.HTTP_200_OK,
        context={
            "page_title": "home",
            "comic": current_comic,
            "comic_img": img_base64,
            "is_current_comic": is_current(comic_num=current_comic.comic_num),
        },
    )

    return template


@router.get("/comics", response_class=HTMLResponse)
def render_comics_page(request: Request) -> HTMLResponse:
    with get_db() as session:
        repo = comic.XKCDComicRepository(session)

        all_comics: list[comic.XKCDComicModel] = repo.get_all()

    comic_img_pairs = []

    for c in all_comics:
        try:
            _img: comic.XKCDComicImage | None = (
                xkcd_comic.comic_img.retrieve_img_from_db(c.comic_num)
            )
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception getting comic #{c.comic_num} from database. Details: {exc}"
            )
            log.error(msg)

            continue

        if _img is None:
            log.warning(f"Image for comic #{c.comic_num} is None. Skipping.")

            try:
                _img = xkcd_comic.comic_img.request_img_from_api(c)
            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception requesting missing image for XKCD comic #{c.comic_num}. Details: {exc}"
                )
                log.error(msg)

                continue

            img_base64 = xkcd_mod.encode_img_bytes(_img)

        else:
            ## Encode img bytes so comic image can be rendered on webpage
            try:
                img_base64 = xkcd_mod.encode_img_bytes(_img.img)
            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception converting XKCD comic #{c.comic_num} image to base64-encoded bytes. Details: {exc}"
                )
                log.error(msg)

                continue

            comic_img_pairs.append({"comic": c, "comic_img": img_base64})

    ## Sort comic_img_pairs by comic_num
    _comic_img_pairs_sorted = sorted(
        comic_img_pairs, key=lambda x: x["comic"].comic_num
    )
    comic_img_pairs = _comic_img_pairs_sorted

    template = templates.TemplateResponse(
        request=request,
        name="pages/comics.html",
        status_code=status.HTTP_200_OK,
        context={
            "page_title": "comics",
            "comic_img_pairs": comic_img_pairs,
            "current_comic_num": xkcd_comic.current_comic.get_current_comic_metadata().comic_num,
        },
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
            "is_current_comic": is_current(comic_num=_comic.comic_num),
        },
    )

    return template


## Keep at bottom to avoid overriding other URLs
@router.get("/comics/{comic_num}", response_class=HTMLResponse)
def render_single_comic_page(request: Request, comic_num: int) -> HTMLResponse:
    if not isinstance(comic_num, int):
        log.error(
            f"Input comic_num '{comic_num}' it not an integer. Type: ({type(comic_num)})"
        )

        ## Build template response
        template = templates.TemplateResponse(
            request=request,
            name="pages/error/default_404.html",
            status_code=status.HTTP_404_NOT_FOUND,
            context={
                "page_title": "NotFound",
                "comic": None,
                "comic_img": None,
                "is_current_comic": False,
            },
        )

        return template

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
        name="pages/single_comic.html",
        status_code=status.HTTP_200_OK,
        context={
            "page_title": f"#{_comic.comic_num}",
            "comic": _comic,
            "comic_img": img_base64,
            "is_current_comic": is_current(comic_num=_comic.comic_num),
        },
    )

    return template


@router.get("/admin", response_class=HTMLResponse)
def render_admin_page(request: Request) -> HTMLResponse:
    ## Get count of comics in db
    with get_db() as session:
        repo = comic.XKCDComicRepository(session)

        all_comics: list[comic.XKCDComicModel] = repo.get_all()

    ## Get current comic
    try:
        current_comic = xkcd_comic.current_comic.get_current_comic()
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting current XKCD comic for home page. Details: {exc}"
        )
        log.error(msg)

        current_comic = None

    ## Attempt to load comic image from db
    try:
        ## Load comic image from database
        comic_img: comic.XKCDComicImage | None = (
            xkcd_comic.comic_img.retrieve_img_from_db(comic_num=current_comic.comic_num)
        )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception loading XKCD comic #{current_comic.comic_num} image from database. Details: {exc}"
        )
        log.error(msg)

    if comic_img is None:
        ## Comic not found in database, request from API and save
        log.warning(f"Comic #{current_comic.comic_num} image not found.")

        comic_img = xkcd_mod.save_comic_img(comic_obj=current_comic.comic_num)

    ## Encode img bytes so comic image can be rendered on webpage
    try:
        img_base64 = xkcd_mod.encode_img_bytes(comic_img.img)
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception converting XKCD comic #{current_comic.comic_num} image to base64-encoded bytes. Details: {exc}"
        )
        log.error(msg)

    ## Count image files saved
    img_list: list[Path] = []
    for p in paths.COMIC_IMG_DIR.rglob("**/*.png"):
        img_list.append(p)

    ## Count serialized responses
    ser_list: list[Path] = []
    for p in paths.SERIALIZE_COMIC_RESPONSES_DIR.rglob("**/*.msgpack"):
        ser_list.append(p)

    ## Count serialized comic objects
    ser_comics_list: list[Path] = []
    for p in paths.SERIALIZE_COMIC_OBJECTS_DIR.rglob("**/*.msgpack"):
        ser_comics_list.append(p)

    img_dir_stat = DirSizeResponse(dir_path=paths.COMIC_IMG_DIR)
    res_serialize_dir_stat = DirSizeResponse(
        dir_path=paths.SERIALIZE_COMIC_RESPONSES_DIR
    )
    comic_serialize_dir_stat = DirSizeResponse(
        dir_path=paths.SERIALIZE_COMIC_OBJECTS_DIR
    )

    dir_stat_list: list[DirSizeResponse] = [
        img_dir_stat,
        res_serialize_dir_stat,
        comic_serialize_dir_stat,
    ]

    ## Prepare template
    template = templates.TemplateResponse(
        request=request,
        name="pages/admin/index.html",
        status_code=status.HTTP_200_OK,
        context={
            "page_title": "admin",
            "db_comic_count": len(all_comics),
            "current_comic": current_comic,
            "comic_img": img_base64,
            "comic_img_count": len(img_list),
            "serialized_responses_count": len(ser_list),
            "serialized_comics_count": len(ser_comics_list),
            "dir_stats_list": dir_stat_list,
        },
    )

    return template
