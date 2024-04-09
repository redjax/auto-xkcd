"""Entrypoint for the pipeline that scrapes XKCD's API for missing comics.

!!! warning

    Make sure you configure a `request_sleep` limit for this pipeline. It's rude to spam XKCD's API!
"""

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
from helpers.validators import validate_hishel_cachetransport
import hishel
import httpx
from loguru import logger as log
from modules import requests_prefab, xkcd_mod
import msgpack
from packages import xkcd_comic
from pipelines import comic_pipelines
from utils import serialize_utils

def run_pipeline(
    cache_transport: hishel.CacheTransport = None,
    request_sleep: int = 5,
    overwrite_serialized_comic: bool = False,
    max_list_size: int = 50,
    loop_limit: int | None = None,
) -> list[XKCDComic]:
    """Start the pipeline to scrape for missing XKCD comics.

    Params:
        cache_transport (hishel.CacheTransport): The cache transport for the request client.
        request_sleep (int): Number of seconds to sleep between requests.
        overwrite_serialized_comic (bool): If `True`, functions that request a comic will overwrite saved
            serialized data, if it exists.
        max_list_size (int): [Default: 50] If the list of missing comics exceeds `max_list_size`, list will be
            broken into smaller "chunks," where each new list will be smaller in size than `max_list_size`.
        loop_limit (int|None): If set to an integer value, scraping will be limited to the number of loops defined in `loop_limit`.

    Returns:
        (list[XKCDComic]): A list of `XKCDComic` objects.

    """
    cache_transport = validate_hishel_cachetransport(cache_transport=cache_transport)

    scraped_comics: list[XKCDComic] = comic_pipelines.pipeline_scrape_missing_comics(
        cache_transport=cache_transport,
        request_sleep=request_sleep,
        overwrite_serialized_comic=overwrite_serialized_comic,
        max_list_size=max_list_size,
        loop_limit=loop_limit,
    )

    return scraped_comics


if __name__ == "__main__":
    base_app_setup(settings=settings)
    log.info(f"[TEST][env:{settings.env}|container:{settings.container_env}] App Start")

    CACHE_TRANSPORT: hishel.CacheTransport = request_client.get_cache_transport()

    run_pipeline(
        cache_transport=CACHE_TRANSPORT,
        request_sleep=5,
        overwrite_serialized_comic=False,
    )
