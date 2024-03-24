from __future__ import annotations

import json
import typing as t

import hishel
import httpx
from loguru import logger as log

def simple_get(
    request: t.Union[str, httpx.Request] = None,
    method: str | None = "GET",
    transport: hishel.CacheTransport = None,
) -> httpx.Response:
    if isinstance(request, str):
        _req = httpx.Request(method=method, url=request)
        request = _req

    try:
        with httpx.Client(transport=transport) as client:
            try:
                res: httpx.Response = client.send(request)
                log.info(f"[{res.status_code}: {res.reason_phrase}]")

                return res
            except Exception as exc:
                msg = Exception(f"Unhandled exception sending request. Details: {exc}")
                log.error(msg)

                raise msg
    except Exception as exc:
        msg = Exception(f"Unhandled exception building request client. Details: {exc}")
        log.error(msg)

        raise msg


def decode_res_content(res: httpx.Response = None):
    assert res, ValueError("Missing httpx Response object")
    assert isinstance(res, httpx.Response), TypeError(
        f"res must be of type httpx.Response. Got type: ({type(res)})"
    )

    try:
        _decode = res.content.decode("utf-8")
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception decoding response content. Details: {exc}"
        )

        raise msg

    try:
        _json = json.loads(_decode)

        return _json
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception loading decoded response content to dict. Details: {exc}"
        )

        raise msg
