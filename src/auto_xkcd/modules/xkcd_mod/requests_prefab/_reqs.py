import typing as t
import json

from modules.xkcd_mod.constants import XKCD_URL_BASE, XKCD_URL_POSTFIX, CURRENT_XKCD_URL

import httpx
from loguru import logger as log


def make_req(
    method: str = "GET",
    url: str = None,
    headers: dict | None = {"Content-Type": "application/json"},
    params: dict | None = None,
    data: t.Union[dict, str] = None,
) -> httpx.Request:
    """Assemble an httpx.Request instance from inputs.

    Params:
        method (str): The request method type, i.e. "GET", "POST", "PUT", "DELETE".
    """
    assert method, ValueError("Missing a request method")
    assert isinstance(method, str), TypeError(
        f"method must be of type str. Got type: ({type(method)})"
    )
    method = method.upper()

    assert url, ValueError("Missing a request URL")
    assert isinstance(url, str), TypeError(
        f"url must be a string. Got type: ({type(url)})"
    )

    if headers:
        assert isinstance(headers, dict), TypeError(
            f"headers should be a dict. Got type: ({type(headers)})"
        )
    if params:
        assert isinstance(params, dict), TypeError(
            f"params should be a dict. Got type: ({type(params)})"
        )
    if data:
        assert isinstance(data, dict) or isinstance(data, str), TypeError(
            f"data should be a Python dict or JSON string. Got type: ({type(data)})"
        )

        if isinstance(data, dict):
            _data: str = json.dumps(data)
            data = _data

    try:
        req: httpx.Request = httpx.Request(
            method=method, url=url, headers=headers, params=params, data=data
        )

        return req

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception building {method} request to URL: {url}. Details: {exc}"
        )
        log.error(msg)

        raise msg


def current_comic_req() -> httpx.Request:
    try:
        req: httpx.Request = make_req(url=CURRENT_XKCD_URL)

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

    log.debug(f"Requesting URL for comic #{comic_num}: {_url}")
    try:
        req: httpx.Request = make_req(url=_url)

        return req
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception building request for comic #{comic_num}. Details: {exc}"
        )
        log.error(msg)

        raise msg
