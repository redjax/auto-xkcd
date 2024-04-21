from core.config import settings
from api.config import api_settings
from api.responses import API_RESPONSES_DICT
from fastapi import APIRouter
from red_utils.ext.fastapi_utils import healthcheck

prefix: str = "/api/v1"

router: APIRouter = APIRouter(prefix=prefix, responses=API_RESPONSES_DICT)

router.include_router(healthcheck.router)
