from __future__ import annotations

from pathlib import Path
import typing as t

from core import request_client
from domain.xkcd import CurrentComicMeta, XKCDComic
from helpers import data_ctl
from helpers.validators import validate_hishel_cachetransport
import hishel
import httpx
from loguru import logger as log
from modules import requests_prefab, xkcd_mod
import msgpack
from pendulum import DateTime
from red_utils.ext import time_utils
from utils import serialize_utils

def _request_current_comic_res(
    cache_transport: hishel.CacheTransport = None,
) -> httpx.Response:
    """Make request for current XKCD comic.

    Params:
        cache_transport (hishel.CacheTransport): A cache transport to use for the request client.

    Returns:
        (httpx.Response): The current comic `Response`.

    """
    cache_transport = validate_hishel_cachetransport(cache_transport=cache_transport)

    try:
        current_comic_req: httpx.Request = requests_prefab.current_comic_req()

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting current XKCD comic request prefab. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    try:
        with request_client.HTTPXController(transport=cache_transport) as httpx_ctl:
            res: httpx.Response = httpx_ctl.send_request(request=current_comic_req)
            log.debug(
                f"Current XKCD comic response: [{res.status_code}: {res.reason_phrase}]"
            )

            if not res.status_code == 200:
                log.warning(
                    f"Non-200 status code: [{res.status_code}: {res.reason_phrase}]: {res.text}"
                )

                raise NotImplementedError(
                    f"Error handling for non-200 status codes not yet implemented."
                )

        log.success(f"Current XKCD comic requested")
        return res

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception requesting current XKCD comic. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc


def save_current_comic_to_db():
    raise NotImplementedError("Saving to database is not yet implemented")


def get_current_comic(
    cache_transport: hishel.CacheTransport = None,
    overwrite_serialized_comic: bool = False,
) -> XKCDComic:
    """Run through operations to get the current XKCD comic.

    Params:
        cache_transport (hishel.CacheTransport): A cache transport for the request client.
        overwrite_serialized_comic (bool): [Default: `False`] If `True`, overwrites serialized comic if it exists.

    Returns:
        (XKCDComic): An instance of `XKCDComic`, with params filled by response data.

    """
    cache_transport = validate_hishel_cachetransport(cache_transport=cache_transport)

    ## Get comic Response
    try:
        current_comic_res: httpx.Response = _request_current_comic_res(
            cache_transport=cache_transport
        )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception building current XKCD comic Request. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    ## Convert httpx.Response into XKCDComic object
    try:
        comic = xkcd_mod.response_handler.convert_comic_response_to_xkcdcomic(
            comic_res=current_comic_res
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
    try:
        data_ctl.update_comic_nums_file(comic_num=comic.num)
    except Exception as exc:
        msg = Exception(f"Unhandled exception updating comic_nums file. Details: {exc}")
        log.error(msg)
        log.trace(exc)

    ## Update current_comic.json file
    try:
        _ts: str | DateTime = time_utils.get_ts()
        current_comic_meta: CurrentComicMeta = CurrentComicMeta(
            comic_num=comic.num, last_updated=_ts
        )

        try:
            data_ctl.update_current_comic_meta(current_comic=current_comic_meta)
            log.success(f"Current comic metadata file updated.")
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception updating current comic metadata file. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            raise exc

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception updating current comic metadata. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    return comic
