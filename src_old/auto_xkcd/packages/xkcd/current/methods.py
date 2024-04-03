from __future__ import annotations

import typing as t

from core import request_client
import hishel
import httpx
from loguru import logger as log
from modules import xkcd_mod
from red_utils.std import hash_utils
from utils import serialize_utils

def request_current_comic(
    transport: hishel.CacheTransport = request_client.CACHE_TRANSPORT,
) -> httpx.Response:
    assert transport, ValueError("Missing reuqest transport")
    assert isinstance(transport, hishel.CacheTransport), TypeError(
        f"transport must be a hishel.CacheTransport object. Got type: ({type(transport)})"
    )

    # req: httpx.Request = xkcd_mod.make_req(url=xkcd_mod.CURRENT_XKCD_URL)
    req: httpx.Request = xkcd_mod.current_comic_req()

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
