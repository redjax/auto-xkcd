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
from pipelines import comic_pipelines

from loguru import logger as log

import httpx
import hishel
import msgpack


def run_pipeline(
    cache_transport: hishel.CacheTransport = None,
    comic_nums: list[int] = None,
    overwrite_serialized_comic: bool = False,
    request_sleep: int = 5,
) -> XKCDComic:
    cache_transport = validate_hishel_cachetransport(cache_transport=cache_transport)
    comic_nums = validate_comic_nums_lst(comic_nums=comic_nums)

    current_comic: XKCDComic = comic_pipelines.pipeline_multiple_comics(
        cache_transport=cache_transport,
        comic_nums=comic_nums,
        overwrite_serialized_comic=overwrite_serialized_comic,
        request_sleep=request_sleep,
    )
    log.debug(f"Current comic ({type(current_comic)}): {current_comic}")

    return current_comic


if __name__ == "__main__":
    base_app_setup(settings=settings)
    log.info(
        f"[env:{settings.env}|container:{settings.container_env}] MULTIPLE COMIC PIPELINE"
    )

    CACHE_TRANSPORT: hishel.CacheTransport = request_client.get_cache_transport()
    DEMO_COMIC_NUMS: list[int] = [1, 10, 25, 42, 58, 79, 96, 404, 500, 1245]
    REQUEST_PAUSE: int = 5

    current_comic: XKCDComic = run_pipeline(
        cache_transport=CACHE_TRANSPORT,
        comic_nums=DEMO_COMIC_NUMS,
        overwrite_serialized_comic=True,
        request_sleep=REQUEST_PAUSE,
    )
