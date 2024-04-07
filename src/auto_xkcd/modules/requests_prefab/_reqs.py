from __future__ import annotations

import json
import typing as t

import httpx
from loguru import logger as log
from core.constants import CURRENT_XKCD_URL, XKCD_URL_BASE, XKCD_URL_POSTFIX
from core import request_client


def current_comic_req() -> httpx.Request:
    try:
        req: httpx.Request = request_client.build_request(url=CURRENT_XKCD_URL)

        return req

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception building current XKCD comic Request object. Details: {exc}"
        )
        log.error(msg)

        raise msg


def comic_num_req(comic_num: t.Union[int, str] = None) -> httpx.Request:
    assert comic_num, ValueError("Missing comic_num")
    assert isinstance(comic_num, int) or isinstance(comic_num, str), TypeError(
        f"comic_num must be an int or str. Got type: ({type(comic_num)})"
    )

    _url: str = f"{XKCD_URL_BASE}/{comic_num}/{XKCD_URL_POSTFIX}"

    # log.debug(f"Requesting URL for comic #{comic_num}: {_url}")
    try:
        req: httpx.Request = request_client.build_request(url=_url)

        return req
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception building request for comic #{comic_num}. Details: {exc}"
        )
        log.error(msg)

        raise msg
