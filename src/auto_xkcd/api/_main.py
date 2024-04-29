from __future__ import annotations

from api._tags import CUSTOM_API_TAGS
from api.config import APISettings, api_settings
from api.routers import admin_router, api_v1_router, frontend_router
from fastapi import APIRouter, FastAPI, status
from fastapi.responses import JSONResponse
from loguru import logger as log

from red_utils.ext.fastapi_utils import tags_metadata, update_tags_metadata

IMPORT_ADMIN_ROUTER: bool = api_settings.include_admin_router
INCLUDE_ROUTERS: list[APIRouter] = [api_v1_router, frontend_router]

if IMPORT_ADMIN_ROUTER:
    INCLUDE_ROUTERS.append(admin_router)

_tags_metadata = update_tags_metadata(
    tags_metadata=tags_metadata, update_metadata=CUSTOM_API_TAGS
)

tags_metadta = _tags_metadata

app: FastAPI = FastAPI(
    title=api_settings.title,
    summary=api_settings.summary,
    description=api_settings.description,
    version=api_settings.version,
    openapi_url=api_settings.openapi_url,
    redirect_slashes=api_settings.redirect_slashes,
    docs_url=api_settings.docs_url,
    redoc_url=api_settings.redoc_url,
    openapi_prefix=api_settings.openapi_prefix,
    root_path=api_settings.root_path,
    root_path_in_servers=api_settings.root_path_in_servers,
    tags=tags_metadata,
)

for _router in INCLUDE_ROUTERS:
    app.include_router(_router)

if IMPORT_ADMIN_ROUTER:
    log.warning("Mounting admin router")
    app.include_router(admin_router)


# @app.get("/")
# def root() -> JSONResponse:
#     log.debug("Root route reached")

#     res: JSONResponse = JSONResponse(
#         status_code=status.HTTP_200_OK, content={"message": "Hello, world!"}
#     )

#     return res
