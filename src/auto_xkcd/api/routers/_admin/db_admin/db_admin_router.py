from __future__ import annotations

from pathlib import Path

from api import helpers as api_helpers
from api.api_responses import API_RESPONSES_DICT, img_response
from api.depends import cache_transport_dependency, db_dependency
from celery.result import AsyncResult
from core import request_client
from core.config import db_settings, settings
from core.constants import IGNORE_COMIC_NUMS, XKCD_URL_BASE, XKCD_URL_POSTFIX
from core.dependencies import get_db
from domain.xkcd import comic
from fastapi import APIRouter, Depends, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
import hishel
from loguru import logger as log
from modules import data_mod, msg_mod, xkcd_mod
from packages import xkcd_comic
from red_utils.ext import time_utils

prefix: str = "/db-admin"
tags: list[str] = ["admin"]

router: APIRouter = APIRouter(prefix=prefix, responses=API_RESPONSES_DICT, tags=tags)

MAX_MULTI_SCRAPE: int = 10


@router.get("/")
def admin_root() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"msg": "Database admin root reached"}
    )


@router.delete("/delete-currentcomic-metadata/{metadata_id}")
def delete_current_comic_metadata(metadata_id: int) -> JSONResponse:
    with get_db() as session:
        repo = comic.CurrentComicMetaRepository(session=session)

        try:
            db_metadata = repo.get_by_id(metadata_id)
            if db_metadata is None:
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={
                        "NotFound": f"Could not find current comic metadata in database with ID '{metadata_id}'."
                    },
                )
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception retrieving current comic metadata from database. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "InternalServerError": f"Unable to retrieve current comic metadta by ID '{metadata_id}'"
                },
            )

        try:
            repo.remove(entity=db_metadata)

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": f"Removed current comic metadata with ID '{metadata_id}'"
                },
            )
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception removing current comic metadata from database. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "InternalServerError": f"Unable to remove current comic metadata by ID '{metadata_id}'."
                },
            )
