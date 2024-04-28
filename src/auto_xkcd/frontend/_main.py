from frontend._tags import CUSTOM_FRONTEND_TAGS

# from frontend.config import FrontendSettings, frontend_settings
from frontend.routers import router as frontend_router

from fastapi import APIRouter, FastAPI, status
from fastapi.responses import JSONResponse, HTMLResponse
from loguru import logger as log

from red_utils.ext.fastapi_utils import tags_metadata, update_tags_metadata

# IMPORT_ADMIN_ROUTER:bool = frontend_settings.include_admin_router
INCLUDE_ROUTERS: list[APIRouter] = []

# if IMPORT_ADMIN_ROUTER:
#     INCLUDE_ROUTERS.append(admin_router)

_tags_metadata = update_tags_metadata(
    tags_metadata=tags_metadata, update_metadata=CUSTOM_FRONTEND_TAGS
)
tags_metadata = _tags_metadata

app: FastAPI = FastAPI(
    title="auto-xckd frontend",
    summary="Frontend app for the site",
    description="...",
    version="0.1.0",
    openapi_url="...",
    redirect_slashes="...",
    docs_url="...",
    redoc_url="...",
    openapi_prefix="...",
    root_path="...",
    root_path_in_servers="...",
    tags_metadata=tags_metadata,
)

for _router in INCLUDE_ROUTERS:
    app.include_router(_router)

# if IMPORT_ADMIN_ROUTER:
#     log.warning("Mounting admin frontend")
#     app.include_router(admin_router)


@app.get("/")
def ui_home() -> HTMLResponse:
    return """
<b>NotImplemented</b>
"""
