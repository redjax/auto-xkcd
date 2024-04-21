from __future__ import annotations

import json
import typing as t

from core import request_client
from core.constants import CURRENT_XKCD_URL, XKCD_URL_BASE, XKCD_URL_POSTFIX
from core.config import telegram_settings, TelegramSettings
import httpx
from loguru import logger as log


def current_comic_req() -> httpx.Request:
    """Build an `httpx.Request` object for the current XKCD comic.

    Returns:
        (httpx.Request): An initialized `httpx.Request` object for the current XKCD comic.

    """
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
    """Build an `httpx.Request` object from an input comic number.

    Params:
        comic_num (int, str): A comic number to request, i.e. 42.

    Returns:
        (httpx.request): An initialized `httpx.Request` for the given `comic_num`.

    """
    assert comic_num, ValueError("Missing comic_num")
    assert isinstance(comic_num, int) or isinstance(comic_num, str), TypeError(
        f"comic_num must be an int or str. Got type: ({type(comic_num)})"
    )

    ## Build URL from input comic_num
    _url: str = f"{XKCD_URL_BASE}/{comic_num}/{XKCD_URL_POSTFIX}"

    # log.debug(f"Requesting URL for comic #{comic_num}: {_url}")
    try:
        ## Build the request
        req: httpx.Request = request_client.build_request(url=_url)

        return req

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception building request for comic #{comic_num}. Details: {exc}"
        )
        log.error(msg)

        raise msg


def comic_img_req(comic_img_url: str = None) -> httpx.Request:
    """Build an `httpx.Request` object from a comic image.

    Params:
        comic_img_url (str): A URL for an XKCD comic's image.

    Returns:
        (httpx.request): An initialized `httpx.Request` for the given `comic_img_url`.

    """
    assert comic_img_url, ValueError("Missing comic_img_url")
    assert isinstance(comic_img_url, str), TypeError(
        f"comic_img_url must be a str. Got type: ({type(comic_img_url)})"
    )

    # log.debug(f"Requesting URL for comic #{comic_num}: {_url}")
    try:
        ## Build the request
        req: httpx.Request = request_client.build_request(url=comic_img_url)

        return req

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception building request for comic image. Details: {exc}"
        )
        log.error(msg)

        raise msg


def telegram_chatid_req(bot_token: str = None):
    _url: str = f"https://api.telegram.org/bot{bot_token}/getUpdates"

    req: httpx.Request = request_client.build_request(url=_url)

    return req
