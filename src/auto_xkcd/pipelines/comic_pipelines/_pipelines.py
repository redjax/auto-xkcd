import typing as t
from pathlib import Path

from core.dependencies import settings
from core import (
    request_client,
    XKCD_URL_POSTFIX,
    XKCD_URL_BASE,
    CURRENT_XKCD_URL,
    SERIALIZE_COMIC_RESPONSES_DIR,
    SERIALIZE_COMIC_OBJECTS_DIR,
    COMIC_IMG_DIR,
)
from domain.xkcd.comic import XKCDComic
from _setup import base_app_setup
from modules import requests_prefab
from modules import xkcd_mod
from utils import serialize_utils
from packages import xkcd_comic
from helpers.validators import validate_hishel_cachetransport, validate_comic_nums_lst

from loguru import logger as log

import httpx
import hishel
import msgpack


def pipeline_current_comic(
    cache_transport: hishel.CacheTransport = None,
    overwrite_serialized_comic: bool = False,
) -> XKCDComic:
    """Pipeline to request & process the current XKCD comic."""
    cache_transport = validate_hishel_cachetransport(cache_transport=cache_transport)

    log.info(">> Start current XKCD comic pipeline")

    try:
        comic: XKCDComic = xkcd_comic.get_current_comic(
            cache_transport=cache_transport,
            overwrite_serialized_comic=overwrite_serialized_comic,
        )
        log.success(f"Current XKCD comic requested")

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception running current XKCD comic pipeline. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    log.info("<< End current XKCD comic pipeline")

    return comic


def pipeline_multiple_comics(
    cache_transport: hishel.CacheTransport = None,
    comic_nums: list[int] = None,
    overwrite_serialized_comic: bool = False,
    request_sleep: int = 5,
) -> list[XKCDComic]:
    cache_transport = validate_hishel_cachetransport(cache_transport=cache_transport)
    comic_nums = validate_comic_nums_lst(comic_nums=comic_nums)

    log.info(">> Start multiple comic pipeline")

    try:
        comics: list[XKCDComic] = xkcd_comic.get_multiple_comics(
            cache_transport=cache_transport,
            comic_nums=comic_nums,
            overwrite_serialized_comic=overwrite_serialized_comic,
            request_sleep=request_sleep,
        )
    except Exception as exc:
        msg = Exception(f"Unhandled exception getting multiple comics. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc

    log.info("<< End multiple comic pipeline")

    return comics


def pipeline_missing_comics(
    cache_transport: hishel.CacheTransport = None,
    overwrite_serialized_comic: bool = False,
    request_sleep: int = 5,
):
    cache_transport = validate_hishel_cachetransport(cache_transport=cache_transport)

    pass
