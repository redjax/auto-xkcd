from __future__ import annotations

from pathlib import Path
import time
import typing as t

from core import request_client
import hishel
import httpx
from loguru import logger as log
from modules import xkcd_mod
from packages.xkcd.helpers import (
    ComicNumsController,
    comic_num_hash,
    get_comic_nums,
    parse_comic_response,
    serialize_response,
    url_hash,
)

def get_comic(
    comic_num: t.Union[str, int] = None,
    save_serial: bool = True,
    transport: hishel.CacheTransport = request_client.CACHE_TRANSPORT,
) -> httpx.Response:
    assert comic_num, ValueError("Missing a comic_num")
    assert isinstance(comic_num, str) or isinstance(comic_num, int), TypeError(
        f"comic_num must be of type str or dict. Got type: ({type(comic_num)})"
    )

    with ComicNumsController() as comic_nums_controller:
        comic_nums = comic_nums_controller.as_list()

    if comic_num in comic_nums:
        log.warning(f"Comic #{comic_num} has already been requested.")

    comic_req: httpx.Request = xkcd_mod.comic_num_req(comic_num=comic_num)

    with transport as transport:
        try:
            res: httpx.Response = request_client.simple_get(
                request=comic_req, transport=transport
            )
            # log.info(
            #     f"Comic #{comic_num} response: [{res.status_code}: {res.reason_phrase}]"
            # )
            _url_hash: str = url_hash(url=res.url)
            log.debug(f"URL hash: {_url_hash}")

            return res

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception requesting comic #{comic_num}. Details: {exc}"
            )
            log.error(msg)

            raise msg


def get_multiple_comics(
    comic_nums_list: list[t.Union[int, str]] = None,
    transport: hishel.CacheTransport = request_client.CACHE_TRANSPORT,
    sleep_duration: int = 5,
) -> list[httpx.Response]:
    assert comic_nums_list, ValueError("Missing list of comic_nums to request")
    assert isinstance(comic_nums_list, list), TypeError(
        f"comic_nums_list must be of type list. Got type: ({type(comic_nums_list)})"
    )

    assert sleep_duration, ValueError("Missing a sleep_duration integer value")
    assert isinstance(sleep_duration, int), TypeError(
        f"sleep_duration must be a non-zero positive integer. Got type: ({type(sleep_duration)})"
    )

    if not transport:
        transport: hishel.CacheTransport = request_client.CACHE_TRANSPORT

    comic_responses: list[httpx.Response] = []

    # with ComicNumsController() as comic_nums_ctl:
    #     comic_nums: list[int] = comic_nums_ctl.as_list()
    comic_nums: list[int] = get_comic_nums()

    for comic_num in comic_nums_list:
        assert comic_num, ValueError("Missing a comic_num")
        assert isinstance(comic_num, str) or isinstance(comic_num, int), TypeError(
            f"comic_num must be of type str or dict. Got type: ({type(comic_num)})"
        )

        if comic_num in comic_nums:
            log.warning(f"Comic #{comic_num} has already been requested")

        req: httpx.Request = xkcd_mod.comic_num_req(comic_num=comic_num)

        log.info(f"Requesting comic #{comic_num}")
        try:
            comic_res: httpx.Response = request_client.simple_get(
                request=req, transport=transport
            )
            # log.info(
            #     f"Comic #{comic_num} response: [{comic_res.status_code}: {comic_res.reason_phrase}]"
            # )
            _url_hash: str = url_hash(url=comic_res.url)
            log.debug(f"URL hash: {_url_hash}")

            comic_responses.append(comic_res)

            with ComicNumsController() as comic_nums_ctl:
                comic_data_dict = {"comic_num": comic_num, "img_saved": False}

                try:
                    comic_nums_ctl.add_comic_num_data(comic_data_dict)
                except Exception as exc:
                    msg = Exception(
                        f"Unhandled exception saving comic number to CSV. Details: {exc}"
                    )
                    log.error(msg)

                    # continue

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception requesting comic #{comic_num}. Details: {exc}"
            )
            log.error(msg)

            raise msg

        if comic_num not in comic_nums:
            log.info(f"Pause for [{sleep_duration}] second(s) between requests...")
            time.sleep(sleep_duration)
        else:
            continue

    return comic_responses
