from __future__ import annotations

from .base import get_namespace

__all__ = [
    "LOGGING_SETTINGS",
    "APP_SETTINGS",
    "DATABASE_SETTINGS",
    "CELERY_SETTINGS",
    "FASTAPI_SETTINGS",
    "UVICORN_SETTINGS",
    "NTFY_SETTINGS",
]

LOGGING_SETTINGS = get_namespace("logging")
APP_SETTINGS = get_namespace("app")
DATABASE_SETTINGS = get_namespace("database")
CELERY_SETTINGS = get_namespace("celery")
FASTAPI_SETTINGS = get_namespace("fastapi")
UVICORN_SETTINGS = get_namespace("uvicorn")
NTFY_SETTINGS = get_namespace("ntfy")
