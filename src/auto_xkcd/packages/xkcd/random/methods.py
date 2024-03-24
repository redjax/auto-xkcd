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


def get_random_comic(save_serial: bool = True):
    with ComicNumsController() as comic_nums:
        highest_comic_num = comic_nums.highest()

    rand_comic_num = random.randint(0, highest_comic_num - 1)

    with request_client.CACHE_TRANSPORT as transport:
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

    try:
        comic_dict: dict = parse_comic_response(res=res)
        comic_hash: str = comic_num_hash(comic_num=comic_dict["num"])
        log.debug(f"Comic num [{comic_dict['num']}] hash: {comic_hash}")

        ## Append hashes to response dict
        comic_dict["url_hash"] = url_hash

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception parsing current XKCD comic response. Details: {exc}"
        )
        log.error(msg)

        raise msg

    if save_serial:
        serial_filename: str = str(comic_dict["num"]) + ".msgpack"

        try:
            log.debug(f"Serialized filename: {serial_filename}")
            serialize_response(res=res, filename=serial_filename)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception serializing comic response. Details: {exc}"
            )
            log.error(msg)

    return comic_dict
