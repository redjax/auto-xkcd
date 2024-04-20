from core.config import settings
from api._config import api_settings
from fastapi import APIRouter
from red_utils.ext.fastapi_utils import healthcheck
from api.routers.test import test_router
from api.routers.comics import comics_router
from api._responses import API_RESPONSES_DICT

prefix: str = "/api/v1"
responses: dict = API_RESPONSES_DICT

router: APIRouter = APIRouter(prefix=prefix, responses=responses)

router.include_router(healthcheck.router)

if settings.env == "dev":
    router.include_router(test_router.router)

router.include_router(comics_router.router)
