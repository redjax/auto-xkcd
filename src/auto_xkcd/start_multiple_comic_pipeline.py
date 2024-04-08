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


def main(cache_transport: hishel.CacheTransport = None) -> XKCDComic:
    cache_transport = validate_hishel_cachetransport(cache_transport=cache_transport)

    current_comic: XKCDComic = comic_pipelines.pipeline_multiple_comics(
        cache_transport=cache_transport
    )
    log.debug(f"Current comic ({type(current_comic)}): {current_comic}")

    return current_comic


if __name__ == "__main__":
    base_app_setup(settings=settings)
    log.info(f"[TEST][env:{settings.env}|container:{settings.container_env}] App Start")

    CACHE_TRANSPORT: hishel.CacheTransport = request_client.get_cache_transport()

    current_comic: XKCDComic = main(cache_transport=CACHE_TRANSPORT)
