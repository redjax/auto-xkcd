import typing as t
from pathlib import Path

from dynaconf import Dynaconf
from loguru import logger as log
from pydantic import Field, field_validator, ValidationError, ConfigDict, computed_field
from pydantic_settings import BaseSettings

DYNACONF_API_SETTINGS: Dynaconf = Dynaconf(
    environments=True,
    envvar_prefix="FASTAPI",
    settings_files=["fastapi/settings.toml", "fastapi/.secrets.toml"],
)

DYNACONF_UVICORN_SETTINGS: Dynaconf = Dynaconf(
    environments=True,
    envvar_prefix="UVICORN",
    settings_files=["uvicorn/settings.toml", "uvicorn/.secrets.toml"],
)


class APISettings(BaseSettings):
    debug: bool = Field(
        default=DYNACONF_API_SETTINGS.FASTAPI_DEBUG, env="FASTAPI_DEBUG"
    )
    title: str = Field(default=DYNACONF_API_SETTINGS.FASTAPI_TITLE, env="FASTAPI_TITLE")
    summary: str = Field(
        default=DYNACONF_API_SETTINGS.FASTAPI_SUMMARY, env="FASTAPI_SUMMARY"
    )
    description: str = Field(
        default=DYNACONF_API_SETTINGS.FASTAPI_DESCRIPTION, env="FASTAPI_DESCRIPTION"
    )
    version: str = Field(
        default=DYNACONF_API_SETTINGS.FASTAPI_VERSION, env="FASTAPI_VERSION"
    )
    openapi_url: str = Field(
        default=DYNACONF_API_SETTINGS.FASTAPI_OPENAPI_URL, env="FASTAPI_OPENAPI_URL"
    )
    redirect_slashes: bool = Field(
        default=DYNACONF_API_SETTINGS.FASTAPI_REDIRECT_SLASHES,
        env="FASTAPI_REDIRECT_SLASHES",
    )
    docs_url: str = Field(
        default=DYNACONF_API_SETTINGS.FASTAPI_DOCS_URL, env="FASTAPI_DOCS_URL"
    )
    redoc_url: str = Field(
        default=DYNACONF_API_SETTINGS.FASTAPI_REDOC_URL, env="FASTAPI_REDOC_URL"
    )
    openapi_prefix: str = Field(
        default=DYNACONF_API_SETTINGS.FASTAPI_OPENAPI_PREFIX,
        env="FASTAPI_OPENAPI_PREFIX",
    )
    root_path: str = Field(
        default=DYNACONF_API_SETTINGS.FASTAPI_ROOT_PATH, env="FASTAPI_ROOT_PATH"
    )
    root_path_in_servers: bool = Field(
        default=DYNACONF_API_SETTINGS.FASTAPI_ROOT_PATH_IN_SERVERS,
        env="FASTAPI_ROOT_PATH_IN_SERVERS",
    )


class UvicornSettings(BaseSettings):
    app: str = Field(default=DYNACONF_UVICORN_SETTINGS.UVICORN_APP, env="UVICORN_APP")
    host: str = Field(
        default=DYNACONF_UVICORN_SETTINGS.UVICORN_HOST, env="UVICORN_HOST"
    )
    port: int = Field(
        default=DYNACONF_UVICORN_SETTINGS.UVICORN_PORT, env="UVICORN_PORT"
    )
    root_path: str = Field(
        default=DYNACONF_UVICORN_SETTINGS.UVICORN_ROOT_PATH, env="UVICORN_ROOT_PATH"
    )
    reload: bool = Field(
        default=DYNACONF_UVICORN_SETTINGS.UVICORN_RELOAD, env="UVICORN_RELOAD"
    )
    log_level: str = Field(
        default=DYNACONF_UVICORN_SETTINGS.UVICORN_LOG_LEVEL, env="UVICORN_LOG_LEVEL"
    )


api_settings: APISettings = APISettings()
uvicorn_settings: UvicornSettings = UvicornSettings()
