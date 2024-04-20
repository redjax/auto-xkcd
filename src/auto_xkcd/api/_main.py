from api._config import api_settings, APISettings
from api.routers import api_v1_router

from fastapi import FastAPI, APIRouter
from loguru import logger as log

INCLUDE_ROUTERS: list[APIRouter] = [api_v1_router]

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
)

app.include_router(api_v1_router)


@app.get("/")
def root():
    log.debug(f"Root route reached")
    return {"msg": "Hello world!"}
