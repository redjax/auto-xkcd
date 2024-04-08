from __future__ import annotations

from pathlib import Path
import time
import typing as t

from core import IGNORE_COMIC_NUMS, request_client
from domain.xkcd import XKCDComic
from helpers import data_ctl
from helpers.validators import validate_comic_nums_lst, validate_hishel_cachetransport
import hishel
import httpx
from loguru import logger as log
from modules import requests_prefab, xkcd_mod
import msgpack
from pendulum import DateTime
from red_utils.ext import time_utils
from utils import serialize_utils

def _request_comic_res(
    cache_transport: hishel.CacheTransport = None, comic_num: int = 0
) -> httpx.Response:
    """Make request for XKCD comic."""
    cache_transport = validate_hishel_cachetransport(cache_transport=cache_transport)

    try:
        comic_req: httpx.Request = requests_prefab.comic_num_req(comic_num=comic_num)

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception requesting comic #{comic_num}. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    try:
        with request_client.HTTPXController(transport=cache_transport) as httpx_ctl:
            res: httpx.Response = httpx_ctl.send_request(request=comic_req)

            if not res.status_code == 200:
                log.warning(
                    f"Non-200 status code for comic #{comic_num}: [{res.status_code}: {res.reason_phrase}]: {res.text}"
                )

                raise NotImplementedError(
                    f"Error handling for non-200 status codes not yet implemented."
                )

        log.success(f"Requested XKCD comic #{comic_num}")
        return res

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception requesting comic #{comic_num}. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc


def get_single_comic(
    cache_transport: hishel.CacheTransport = None,
    comic_num: int = None,
    overwrite_serialized_comic: bool = False,
) -> XKCDComic:
    cache_transport = validate_hishel_cachetransport(cache_transport=cache_transport)

    if comic_num in IGNORE_COMIC_NUMS:
        log.warning(f"Comic #{comic_num} is in list of ignored comic numbers. Skipping")

        return None

    ## Get comic Response
    try:
        comic_res: httpx.Response = _request_comic_res(
            cache_transport=cache_transport, comic_num=comic_num
        )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting comic #{comic_num}. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    ## Convert httpx.Response into XKCDComic object
    try:
        comic = xkcd_mod.response_handler.convert_comic_response_to_xkcdcomic(
            comic_res=comic_res
        )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception converting httpx.Response to XKCDComic object. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    ## Save comic image
    try:
        comic: XKCDComic = xkcd_mod.request_and_save_comic_img(
            comic=comic, cache_transport=cache_transport
        )
        log.success(f"Comic #{comic.num} image saved.")

        SERIALIZE_COMIC: bool = True
    except Exception as exc:
        msg = Exception(f"Unhandled exception saving comic image. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        SERIALIZE_COMIC: bool = False

    if SERIALIZE_COMIC:
        log.info(f"Serializing XKCDComic object for comic #{comic.num}")

        ## Serialize XKCDComic object
        try:
            xkcd_mod.save_serialize_comic_object(
                comic=comic, overwrite=overwrite_serialized_comic
            )
            log.success(f"Serialized XKCDComic object to file")
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception saving XKCDComic to serialized file. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

    ## Update comic_nums.txt file
    log.debug(f"Updating comic_nums.txt file")
    try:
        data_ctl.update_comic_nums_file(comic_num=comic.num)
    except Exception as exc:
        msg = Exception(f"Unhandled exception updating comic_nums file. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc

    return comic


def get_multiple_comics(
    cache_transport: hishel.CacheTransport = None,
    comic_nums: list[int] = None,
    overwrite_serialized_comic: bool = False,
    request_sleep: int = 5,
) -> list[XKCDComic]:
    cache_transport = validate_hishel_cachetransport(cache_transport=cache_transport)

    saved_comic_nums: list[int] = data_ctl.get_saved_imgs()
    saved_comic_nums = validate_comic_nums_lst(comic_nums=saved_comic_nums)

    comics: list[XKCDComic] = []

    for comic_num in comic_nums:
        if comic_num in IGNORE_COMIC_NUMS:
            log.warning(f"Comic #{comic_num} is in list of ignored comics. Skipping")

            continue

        if comic_num in saved_comic_nums:
            log.warning(f"Comic #{comic_num} has already been downloaded. Skipping.")
            continue

        try:
            _comic: XKCDComic = get_single_comic(
                cache_transport=cache_transport,
                comic_num=comic_num,
                overwrite_serialized_comic=overwrite_serialized_comic,
            )
            comics.append(_comic)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception requesting comic #{comic_num}. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            continue

        log.info(f"Waiting [{request_sleep}]s between requests ...")
        time.sleep(request_sleep)

    if comics:
        ## Suppress debug messaged on large comic list
        if len(comics) < 50:
            log.debug(f"Downloaded [{len(comics)}] comic(s)")

    return comics
