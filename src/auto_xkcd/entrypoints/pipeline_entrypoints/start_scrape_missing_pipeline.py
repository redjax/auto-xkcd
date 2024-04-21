"""Entrypoint for the pipeline that scrapes XKCD's API for missing comics.

!!! warning

    Make sure you configure a `request_sleep` limit for this pipeline. It's rude to spam XKCD's API!
"""

from __future__ import annotations

from pathlib import Path
import time
import typing as t

from setup import base_app_setup
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
    loop_pause: int = 10,
) -> list[XKCDComic]:
    """Start the pipeline to scrape for missing XKCD comics.

    Params:
        cache_transport (hishel.CacheTransport): The cache transport for the request client.
        request_sleep (int): Number of seconds to sleep between requests.
        overwrite_serialized_comic (bool): If `True`, functions that request a comic will overwrite saved
            serialized data, if it exists.
        max_list_size (int): [Default: 50] If the list of missing comics exceeds `max_list_size`, list will be
            broken into smaller "chunks," where each new list will be smaller in size than `max_list_size`.
        loop_limit (int|None): [Default: None] Number of times to loop request. `None` will loop once and return, `0` will loop indefinitely.
        loop_pause (int): [Default: 21600 (6 hours)] Number of seconds to pause between loops.

    Returns:
        (list[XKCDComic]): A list of `XKCDComic` objects.

    """
    cache_transport = validate_hishel_cachetransport(cache_transport=cache_transport)

    LOOP_COUNT: int = 1
    CONTINUE_LOOP: bool = True

    if loop_limit is None:
        log.debug(f"Running scrape for missing comics 1 time")
        scraped_comics: list[XKCDComic] = (
            comic_pipelines.pipeline_scrape_missing_comics(
                cache_transport=cache_transport,
                request_sleep=request_sleep,
                overwrite_serialized_comic=overwrite_serialized_comic,
                max_list_size=max_list_size,
                loop_limit=loop_limit,
            )
        )

        return scraped_comics

    if loop_limit == 0:
        log.debug(f"Looping scraper indefinitely.")
        ## No loop limit, continue looping indefinitely
        scraped_comics: list[XKCDComic] = (
            comic_pipelines.pipeline_scrape_missing_comics(
                cache_transport=cache_transport,
                request_sleep=request_sleep,
                overwrite_serialized_comic=overwrite_serialized_comic,
                max_list_size=max_list_size,
                loop_limit=loop_limit,
            )
        )

        log.info(f"Pause [{loop_pause}] second(s) between scrape loops ...")
        time.sleep(loop_pause)

    else:
        ## Maximum number of loops is specified, loop until threshold reached.
        log.debug(f"Looping scraper [{loop_limit}] time(s).")
        while CONTINUE_LOOP:
            if LOOP_COUNT >= loop_limit:
                CONTINUE_LOOP = False

                continue

            else:
                scraped_comics: list[XKCDComic] = (
                    comic_pipelines.pipeline_scrape_missing_comics(
                        cache_transport=cache_transport,
                        request_sleep=request_sleep,
                        overwrite_serialized_comic=overwrite_serialized_comic,
                        max_list_size=max_list_size,
                        loop_limit=loop_limit,
                    )
                )

            LOOP_COUNT += 1
            log.info(
                f"Pause for [{loop_pause}] second(s) between current comic requests..."
            )
            time.sleep(loop_pause)

        log.info(f"Looped [{LOOP_COUNT}/{loop_limit}] time(s).")

    return scraped_comics


if __name__ == "__main__":
    base_app_setup(settings=settings)
    log.info(f"[TEST][env:{settings.env}|container:{settings.container_env}] App Start")

    CACHE_TRANSPORT: hishel.CacheTransport = request_client.get_cache_transport()

    run_pipeline(
        cache_transport=CACHE_TRANSPORT,
        request_sleep=5,
        overwrite_serialized_comic=False,
        loop_limit=10,
        loop_pause=30,
    )
