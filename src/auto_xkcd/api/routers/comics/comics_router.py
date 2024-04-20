import typing as t

from api._responses import API_RESPONSES_DICT
from api._depends import cache_transport_dependency, db_dependency
from core import request_client
from domain.xkcd import comic
from helpers import data_ctl
from modules import data_mod, xkcd_mod, msg_mod
from packages import xkcd_comic, data_tools, msg
from core.config import settings, db_settings

from loguru import logger as log
from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response


import hishel

prefix: str = "/comics"
tags: list[str] = ["comic"]

router: APIRouter = APIRouter(prefix=prefix, responses=API_RESPONSES_DICT, tags=tags)


@router.get("/current")
def current_comic(
    cache_transport: cache_transport_dependency, db_session: db_dependency
) -> JSONResponse:

    with data_ctl.CurrentComicController() as current_comic_ctl:
        _current_comic_dict = current_comic_ctl.read()

        current_comic_num = _current_comic_dict["comic_num"]

    with db_session as session:
        repo = comic.XKCDComicRepository(session=session)

        try:
            current_comic = repo.get_by_num(current_comic_num)
            log.debug(
                f"Retrieved current comic ({type(current_comic)}): {current_comic}"
            )
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception getting current comic from database. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            raise exc

    # try:
    #     current_comic: comic.XKCDComic = xkcd_comic.get_current_comic(
    #         cache_transport=cache_transport, overwrite_serialized_comic=True
    #     )

    #     res = JSONResponse(
    #         status_code=status.HTTP_200_OK,
    #         content=current_comic.model_dump(exclude={"img_bytes"}),
    #     )

    #     return res

    # except Exception as exc:
    #     msg = Exception(
    #         f"Unhandled exception getting current XKCD comic. Details: {exc}"
    #     )
    #     log.error(msg)
    #     log.trace(exc)

    #     res: JSONResponse = JSONResponse(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         content={"error": "Internal Server Error while getting current XKCD comic"},
    #     )

    #     return res


@router.get("/comic/{comic_num}")
def specific_comic(
    comic_num: int, cache_transport: cache_transport_dependency
) -> JSONResponse:
    try:
        _comic: comic.XKCDComic = xkcd_comic.get_single_comic(
            cache_transport=cache_transport,
            comic_num=comic_num,
            overwrite_serialized_comic=True,
        )

        res = JSONResponse(
            status_code=status.HTTP_200_OK,
            content=_comic.model_dump(exclude={"img_bytes"}),
        )

        return res
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting comic #{comic_num}. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        res: JSONResponse = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": f"Internal Server Error while getting comic #{comic_num}"
            },
        )

        return res
