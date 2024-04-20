import typing as t
from api._config import api_settings
from api._responses import API_RESPONSES_DICT
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from loguru import logger as log

prefix: str = "/testing"
tags: list[str] = ["testing"]

router: APIRouter = APIRouter(prefix=prefix, responses=API_RESPONSES_DICT, tags=tags)


@router.get("/")
def testing_root() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"message": "/testing root reached"}
    )
