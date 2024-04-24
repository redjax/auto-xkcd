from __future__ import annotations

from api.config import api_settings
from api.api_responses import API_RESPONSES_DICT

from .comics import comics_router
from .tasks import tasks_router

from core.config import settings
from fastapi import APIRouter
from red_utils.ext.fastapi_utils import healthcheck

from loguru import logger as log

prefix: str = "/api/v1"

router: APIRouter = APIRouter(prefix=prefix, responses=API_RESPONSES_DICT)

router.include_router(healthcheck.router)
router.include_router(comics_router.router)
router.include_router(tasks_router.router)

if settings.env == "dev":
    from .test import test_router

    log.info("[DEV ENVIRONMENT] Mounting /test endpoint")
    router.include_router(test_router.router)
