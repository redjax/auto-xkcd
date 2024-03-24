from __future__ import annotations

import typing as t

from core import request_client
import hishel
import httpx
from loguru import logger as log
from modules import xkcd_mod
from red_utils.std import hash_utils
from utils import serialize_utils

def build_request(
    method: str = "GET",
    url: str = None,
    headers: dict = {"Content-Type": "application/json"},
) -> httpx.Request:
    assert method, ValueError("Missing a request method")
    assert isinstance(method, str), TypeError(
        f"method must be of type str. Got type: ({type(method)})"
    )
    method = method.upper()

    assert url, ValueError("Missing a request URL")
    assert isinstance(url, str), TypeError(
        f"url must be a string. Got type: ({type(url)})"
    )

    try:
        req: httpx.Request = httpx.Request(method=method, url=url, headers=headers)

        return req

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception building {method} request to URL: {url}. Details: {exc}"
        )

        raise msg


def request_current_comic(
    transport: hishel.CacheTransport = request_client.CACHE_TRANSPORT,
) -> httpx.Response:
    assert transport, ValueError("Missing reuqest transport")
    assert isinstance(transport, hishel.CacheTransport), TypeError(
        f"transport must be a hishel.CacheTransport object. Got type: ({type(transport)})"
    )

    req: httpx.Request = build_request(url=xkcd_mod.CURRENT_XKCD_URL)

    try:
        res: httpx.Response = request_client.simple_get(
            transport=transport, request=req
        )
    except Exception as exc:
        msg = Exception(f"Unhandled exception making request. Details: {exc}")

        log.error(msg)

        raise msg

    if not res.status_code == 200:
        msg = (
            f"Non-200 status code: [{res.status_code}: {res.reason_phrase}] {res.text}"
        )

        log.warning(msg)

        raise Exception(f"{msg}")

    log.info(f"Current comic response: [{res.status_code}: {res.reason_phrase}]")

    return res


def parse_current_comic_response(res: httpx.Response = None) -> dict:
    content: dict = request_client.decode_res_content(res=res)

    return content
