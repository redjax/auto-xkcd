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
from helpers.validators import validate_hishel_cachetransport
from pipelines import comic_pipelines

from loguru import logger as log

import httpx
import hishel
import msgpack


def run_pipeline(
    cache_transport: hishel.CacheTransport = None,
    request_sleep: int = 5,
    overwrite_serialized_comic: bool = False,
    max_list_size: int = 50,
    loop_limit: int | None = None,
) -> list[XKCDComic]:
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
