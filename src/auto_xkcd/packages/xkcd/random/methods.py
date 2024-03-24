import typing as t
from pathlib import Path
import random

from core import request_client
from modules import xkcd_mod
from packages.xkcd.helpers import (
    ComicNumsController,
    url_hash,
    parse_comic_response,
    comic_num_hash,
    serialize_response,
)

from loguru import logger as log
import httpx
import hishel


def get_random_comic(
    transport: hishel.CacheTransport = request_client.CACHE_TRANSPORT,
) -> httpx.Response:
    with ComicNumsController() as comic_nums:
        highest_comic_num = comic_nums.highest()

    rand_comic_num = random.randint(0, highest_comic_num - 1)

    with transport as transport:
        req: httpx.Request = xkcd_mod.comic_num_req(comic_num=rand_comic_num)

        try:
            res: httpx.Response = request_client.simple_get(
                request=req, transport=transport
            )
            log.info(
                f"Comic #{rand_comic_num} response: [{res.status_code}: {res.reason_phrase}]"
            )
            _url_hash: str = url_hash(url=res.url)
            log.debug(f"URL hash: {_url_hash}")

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception getting comic #{rand_comic_num}. Details: {exc}"
            )
            log.error(msg)

    return res
