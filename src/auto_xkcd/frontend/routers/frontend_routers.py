from __future__ import annotations

from api.api_responses import API_RESPONSES_DICT
from api.config import api_settings
from core.config import settings
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from loguru import logger as log
from red_utils.ext.fastapi_utils import healthcheck

from frontend.pages import page_home

prefix: str = "/ui"

tags: list[str] = ["frontend"]

router: APIRouter = APIRouter(prefix=prefix, responses=API_RESPONSES_DICT, tags=tags)

router.include_router(healthcheck.router)


@router.get("/", response_class=HTMLResponse)
def ui_home():
    return page_home.render_page_home()
