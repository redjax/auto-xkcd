from core.config import settings
from api.api_config import api_settings
from fastapi import APIRouter
from red_utils.ext.fastapi_utils import healthcheck
from api.routers.test import test_router

prefix: str = "/api/v1"
responses: dict = {404: {"description": "Not found"}}

router: APIRouter = APIRouter(prefix=prefix, responses=responses)

router.include_router(healthcheck.router)

if settings.env == "dev":
    router.include_router(test_router.router)
