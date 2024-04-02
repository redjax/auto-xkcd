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
            except httpx.ConnectTimeout as _timeout:
                msg = Exception(f"Connection timed out. Details: {_timeout}")
                log.error(msg)

                raise _timeout
            except Exception as exc:
                msg = Exception(f"Unhandled exception sending request. Details: {exc}")
                log.error(msg)

                raise exc

    except httpx.ConnectError as _conn:
        msg = Exception(f"Error while making remote connection. Details: {exc}")
        log.error(msg)

        raise _conn
    except Exception as exc:
        msg = Exception(f"Unhandled exception building request client. Details: {exc}")
        log.error(msg)

        raise exc


def decode_res_content(res: httpx.Response = None):
    assert res, ValueError("Missing httpx Response object")
    assert isinstance(res, httpx.Response), TypeError(
        f"res must be of type httpx.Response. Got type: ({type(res)})"
    )

    _content: bytes = res.content
    assert _content, ValueError("Response content is empty")
    assert isinstance(_content, bytes), TypeError(
        f"Expected response.content to be a bytestring. Got type: ({type(_content)})"
    )

    try:
        _decode = res.content.decode("utf-8")
    except Exception as exc:
        msg = Exception(
            f"[Attempt 1/2] Unhandled exception decoding response content. Details: {exc}"
        )
        log.warning(msg)

        if not res.encoding == "utf-8":
            log.warning(
                f"Retrying response content decode with encoding '{res.encoding}'"
            )
            try:
                _decode = res.content.decode(res.encoding)
            except Exception as exc:
                inner_msg = Exception(
                    f"[Attempt 2/2] Unhandled exception decoding response content. Details: {exc}"
                )
                log.error(inner_msg)

                raise inner_msg

        else:
            log.warning(
                f"Detected UTF-8 encoding, but decoding as UTF-8 failed. Retrying with encoding ISO-8859-1."
            )
            try:
                _decode = res.content.decode("ISO-8859-1")
            except Exception as exc:
                msg = Exception(
                    f"Failure attempting to decode content as UTF-8 and ISO-8859-1. Details: {exc}"
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
