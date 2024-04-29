from __future__ import annotations

from pathlib import Path
import typing as t

from api import helpers as api_helpers

# from api.api_responses import API_RESPONSES_DICT, img_response
from api.routers._frontend._responses import FRONTEND_RESPONSES_DICT
from api.depends import cache_transport_dependency, db_dependency
from .methods import count_total_comics

# from celery.result import AsyncResult
# import celeryapp
from core import request_client
from core.config import db_settings, settings
from core.constants import XKCD_URL_BASE, XKCD_URL_POSTFIX
from domain.xkcd import comic
from fastapi import APIRouter, Depends, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import (
    FileResponse,
    JSONResponse,
    Response,
    StreamingResponse,
    HTMLResponse,
)
from fastapi.templating import Jinja2Templates
import hishel
from loguru import logger as log
from modules import data_mod, msg_mod, xkcd_mod
from packages import xkcd_comic
from red_utils.ext import time_utils

if not Path("auto_xkcd/templates").exists():
    raise FileNotFoundError("Directory not found: 'templates'")
else:
    log.debug("Found templates dir.")
    templates = Jinja2Templates(directory="auto_xkcd/templates")

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
    count_comics = count_total_comics()
    template = templates.TemplateResponse(
        request=request,
        name="pages/comics_all.html",
        status_code=status.HTTP_200_OK,
        context={"page_title": "all comics", "count": count_comics},
    )

    return template


@router.get("/comics/random", response_class=HTMLResponse)
def render_random_comics_page(request: Request) -> HTMLResponse:
    template = templates.TemplateResponse(
        request=request,
        name="pages/comics_random.html",
        status_code=status.HTTP_200_OK,
        context={"page_title": "random comic"},
    )

    return template
