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


def main(cache_transport: hishel.CacheTransport = None):
    cache_transport = validate_hishel_cachetransport(cache_transport=cache_transport)

    comic: XKCDComic = xkcd_comic.get_current_comic(
        cache_transport=cache_transport, overwrite_serialized_comic=True
    )
    log.debug(f"Comic: {comic}")
    # deserialized_comic: XKCDComic | None = xkcd_mod.load_serialized_comic(
    #     comic_num=comic.num
    # )
    # log.debug(f"Deserialized comic ({type(deserialized_comic)}): {deserialized_comic}")

    # comic: XKCDComic = xkcd_comic.get_single_comic(
    #     cache_transport=cache_transport, overwrite_serialized_comic=True, comic_num=42
    # )
    # log.debug(f"Comic #42: {comic}")

    # comic: XKCDComic = xkcd_comic.get_single_comic(
    #     cache_transport=cache_transport, overwrite_serialized_comic=True, comic_num=42
    # )
    # log.debug(f"Comic #{comic.num}: {comic}")

    # comics: list[XKCDComic] = comic_pipelines.pipeline_multiple_comics(
    #     cache_transport=cache_transport,
    #     comic_nums=[1, 24, 86, 92, 320, 500, 555, 615, 645, 720, 732],
    #     request_sleep=5,
    # )


if __name__ == "__main__":
    base_app_setup(settings=settings)
    log.info(f"[TEST][env:{settings.env}|container:{settings.container_env}] App Start")

    CACHE_TRANSPORT: hishel.CacheTransport = request_client.get_cache_transport()

    # current_comic: XKCDComic = comic_pipelines.pipeline_current_comic(
    #     cache_transport=CACHE_TRANSPORT
    # )
    # log.debug(f"Current comic ({type(current_comic)}): {current_comic}")

    main(cache_transport=CACHE_TRANSPORT)
