"""Comic pipelines for interacting with the XKCD API & handling the response."""

from __future__ import annotations

from pathlib import Path
import typing as t

from _setup import base_app_setup
from core import (
    COMIC_IMG_DIR,
    CURRENT_XKCD_URL,
    SERIALIZE_COMIC_OBJECTS_DIR,
    SERIALIZE_COMIC_RESPONSES_DIR,
    XKCD_URL_BASE,
    XKCD_URL_POSTFIX,
    request_client,
)
from core.dependencies import settings
from domain.xkcd.comic import XKCDComic
from helpers.validators import validate_comic_nums_lst, validate_hishel_cachetransport
import hishel
import httpx
from loguru import logger as log
from modules import requests_prefab, xkcd_mod
import msgpack
from packages import xkcd_comic
from utils import serialize_utils


def pipeline_current_comic(
    cache_transport: hishel.CacheTransport = None,
    overwrite_serialized_comic: bool = False,
) -> XKCDComic:
    """Pipeline to request & process the current XKCD comic.

    Params:
        cache_transport (hishel.CacheTransport): A cache transport for the request client.
        overwrite_serialized_comic (bool): If `True`, overwrite existing serialized file with data from request.

    Returns:
        (XKCDComic): The current XKCD comic.

    """
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
    """Pipeline to request multiple comics at once.

    Params:
        cache_transport (hishel.CacheTransport): A cache transport for the request client.
        comic_nums (list[int]): A list of comic numbers to download/process.
        overwrite_serialized_comic (bool): If `True`, overwrite existing serialized file with data from request.
        request_sleep (int): [Default: 5] Number of seconds to sleep between requests.

    Returns:
        (list[XKCDComic]): A list of the requested XKCD comics.

    """
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


def pipeline_scrape_missing_comics(
    cache_transport: hishel.CacheTransport = None,
    overwrite_serialized_comic: bool = False,
    request_sleep: int = 5,
    max_list_size: int = 50,
    loop_limit: int | None = None,
) -> list[XKCDComic]:
    """Pipeline to find & download missing comic images.

    Todo:
        Configurable scrape limits, like a maximum list size.

    Params:
        cache_transport(hishel.CacheTransport): A cache transport for the request client.
        overwrite_serialized_comic (bool): If `True`, overwrite existing serialized file with data from request.
        request_sleep (int): [Default: 5] Number of seconds to sleep between requests.
        max_list_size (int): [Default: 50] If list size exceeds `max_list_size`, break list into smaller "chunks,"
            then return a "list of lists", where each inner list is a "chunk" of 50 comic images.
        loop_limit (int|None): [Default: None] Maximum number of times to loop, regardless of total number of missing comics.

    """
    cache_transport = validate_hishel_cachetransport(cache_transport=cache_transport)

    log.info(">> Start scrape missing comics pipeline")

    try:
        scraped_comics: list[XKCDComic] = xkcd_comic.comic.scrape_missing_comics(
            cache_transport=cache_transport,
            request_sleep=request_sleep,
            max_list_size=max_list_size,
            loop_limit=loop_limit,
            overwrite_serialized_comic=overwrite_serialized_comic,
        )

    except Exception as exc:
        msg = Exception(f"Unhandled exception scraping missing comics. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc

    log.info("<< End scrape missing comics pipeline")

    return scraped_comics
