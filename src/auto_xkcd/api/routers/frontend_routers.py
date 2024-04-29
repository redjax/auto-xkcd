from __future__ import annotations

from ._frontend import frontend_pages_router

# from .comics import comics_router
# from .tasks import tasks_router

# from api.api_responses import API_RESPONSES_DICT
# from api.config import api_settings
from api.routers._frontend._responses import FRONTEND_RESPONSES_DICT
from core.config import settings
from fastapi import APIRouter
from loguru import logger as log
from red_utils.ext.fastapi_utils import healthcheck

# prefix: str = "/api/v1"

tags: list[str] = ["frontend"]

router: APIRouter = APIRouter(responses=FRONTEND_RESPONSES_DICT, tags=tags)

router.include_router(healthcheck.router)
router.include_router(frontend_pages_router.router)
# router.include_router(comics_router.router)
# router.include_router(tasks_router.router)

# if settings.env == "dev":
#     from .test import test_router

#     log.info("[DEV ENVIRONMENT] Mounting /test endpoint")
#     router.include_router(test_router.router)
