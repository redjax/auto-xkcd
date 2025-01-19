from __future__ import annotations

from pathlib import Path

from .db_admin import db_admin_router

from api import helpers as api_helpers
from api.api_responses import API_RESPONSES_DICT, img_response
from api.depends import cache_transport_dependency, db_dependency
from celery.result import AsyncResult
from core import request_client
from core.config import db_settings, settings
from core.constants import IGNORE_COMIC_NUMS, XKCD_URL_BASE, XKCD_URL_POSTFIX
from core.dependencies import get_db
from domain.xkcd import comic
from fastapi import APIRouter, Depends, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
import hishel
from loguru import logger as log
from modules import data_mod, msg_mod, xkcd_mod
from packages import xkcd_comic
from red_utils.ext import time_utils

prefix: str = "/admin"
tags: list[str] = ["admin"]

router: APIRouter = APIRouter(prefix=prefix, responses=API_RESPONSES_DICT, tags=tags)

MAX_MULTI_SCRAPE: int = 10

router.include_router(db_admin_router.router)
