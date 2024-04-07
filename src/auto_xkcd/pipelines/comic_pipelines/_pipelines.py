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
