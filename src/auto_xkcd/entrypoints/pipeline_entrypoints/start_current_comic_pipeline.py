"""Entrypoint for the pipeline that requests the current XKCD comic.

If the current XKCD comic has been requested recently, re-use the response until it is "stale."

"""

from __future__ import annotations

from pathlib import Path
import time
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
    overwrite_serialized_comic: bool = False,
    loop_limit: int | None = None,
    loop_pause: int = 21600,
) -> XKCDComic:
    """Run the pipeline that requests the current XKCD comic.

    Params:
        cache_transport (hishel.CacheTransport): A cache transport for the request client.
        overwrite_serialized_comic (bool): If `True`, functions that request a comic will overwrite saved
            serialized data, if it exists.
        max_list_size (int): [Default: 50] If the list of missing comics exceeds `max_list_size`, list will be
            broken into smaller "chunks," where each new list will be smaller in size than `max_list_size`.
        loop_limit (int|None): [Default: None] Number of times to loop request. `None` will loop once and return, `0` will loop indefinitely.
        loop_pause (int): [Default: 21600 (6 hours)] Number of seconds to pause between loops.

    Returns:
        (XKCDComic): An `XKCDComic` object of the current live XKCD comic.

    """
    cache_transport = validate_hishel_cachetransport(cache_transport=cache_transport)

    LOOP_COUNT: int = 1
    CONTINUE_LOOP: bool = True

    if loop_limit is None:
        log.debug(f"Getting current comic.")

        current_comic: XKCDComic = comic_pipelines.pipeline_current_comic(
            cache_transport=cache_transport,
            overwrite_serialized_comic=overwrite_serialized_comic,
        )
        log.debug(f"Current comic ({type(current_comic)}): {current_comic}")

        return current_comic

    if loop_limit == 0:
        log.debug(f"Looping current comic request indefinitely.")
        ## No loop limit, continue looping indefinitely

        current_comic: XKCDComic = comic_pipelines.pipeline_current_comic(
            cache_transport=cache_transport,
            overwrite_serialized_comic=overwrite_serialized_comic,
        )
        log.debug(f"Current comic ({type(current_comic)}): {current_comic}")

        log.info(
            f"Pause for [{loop_pause}] second(s) between current comic requests..."
        )
        time.sleep(loop_pause)

    else:
        ## Maximum number of loops is specified, loop until threshold reached.
        log.debug(f"Looping current comic request [{loop_limit}] time(s).")
        while CONTINUE_LOOP:
            if LOOP_COUNT >= loop_limit:
                CONTINUE_LOOP = False

                continue

            else:
                current_comic: XKCDComic = comic_pipelines.pipeline_current_comic(
                    cache_transport=cache_transport,
                    overwrite_serialized_comic=overwrite_serialized_comic,
                )
                log.debug(f"Current comic ({type(current_comic)}): {current_comic}")

            LOOP_COUNT += 1
            log.info(
                f"Pause for [{loop_pause}] second(s) between current comic requests..."
            )
            time.sleep(loop_pause)

        log.info(f"Looped [{LOOP_COUNT}/{loop_limit}] time(s).")

    return current_comic


if __name__ == "__main__":
    base_app_setup(settings=settings)
    log.info(
        f"[env:{settings.env}|container:{settings.container_env}] CURRENT COMIC PIPELINE"
    )

    CACHE_TRANSPORT: hishel.CacheTransport = request_client.get_cache_transport()

    current_comic: XKCDComic = run_pipeline(
        cache_transport=CACHE_TRANSPORT, loop_limit=0
    )
