"""Entrypoint for the pipeline that requests the current XKCD comic.

If the current XKCD comic has been requested recently, re-use the response until it is "stale."

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

def run_pipeline(cache_transport: hishel.CacheTransport = None) -> XKCDComic:
    """Run the pipeline that requests the current XKCD comic.

    Params:
        cache_transport (hishel.CacheTransport): A cache transport for the request client.

    Returns:
        (XKCDComic): An `XKCDComic` object of the current live XKCD comic.

    """
    cache_transport = validate_hishel_cachetransport(cache_transport=cache_transport)

    current_comic: XKCDComic = comic_pipelines.pipeline_current_comic(
        cache_transport=CACHE_TRANSPORT
    )
    log.debug(f"Current comic ({type(current_comic)}): {current_comic}")

    return current_comic


if __name__ == "__main__":
    base_app_setup(settings=settings)
    log.info(
        f"[env:{settings.env}|container:{settings.container_env}] CURRENT COMIC PIPELINE"
    )

    CACHE_TRANSPORT: hishel.CacheTransport = request_client.get_cache_transport()

    current_comic: XKCDComic = run_pipeline(
        cache_transport=CACHE_TRANSPORT,
    )
