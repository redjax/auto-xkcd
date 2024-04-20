import typing as t
from api.api_config import api_settings
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from loguru import logger as log

prefix: str = "/testing"
responses: dict = {404: {"description": "Not found"}}
tags: list[str] = ["testing"]

router: APIRouter = APIRouter(prefix=prefix, responses=responses, tags=tags)


@router.get("/")
def testing_root() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"message": "/testing root reached"}
    )
