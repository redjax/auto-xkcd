import typing as t
from pathlib import Path
import json

from contextlib import contextmanager, AbstractContextManager

import httpx
import hishel

## For auto detecting response character set
import chardet

from loguru import logger as log

CURRENT_COMIC_URL: str = "https://xkcd.com/info.0.json"

_client = httpx.Client()
_client


def autodetect_charset(content: bytes = None):
    try:
        _encoding = chardet.detect(byte_str=content).get("encoding")

        return _encoding

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception auto-detecting character set for input bytestring. Details: {exc}"
        )
        log.error(msg)
        log.warning("Defaulting to utf-8")

        return "utf-8"


class HTTPXController(AbstractContextManager):
    def __init__(
        self,
        url: str | None = None,
        base_url: str | None = None,
        proxy: str | None = None,
        proxies: dict[str, str] | None = None,
        mounts: dict[str, httpx.HTTPTransport] | None = {},
        cookies: dict[str, t.Any] | None = {},
        auth: httpx.Auth | None = None,
        headers: dict[str, str] | None = {},
        params: dict[str, t.Any] | None = {},
        follow_redirects: bool = False,
        max_redirects: int | None = 20,
        timeout: t.Union[int, float] | None = 60,
        limits: httpx.Limits | None = None,
        transport: httpx.HTTPTransport | hishel.CacheTransport | None = None,
        default_encoding: str = autodetect_charset,
    ):
        self.url: httpx.URL | None = httpx.URL(url) if url else None
        self.base_url: httpx.URL | None = httpx.URL(base_url) if base_url else None
        self.proxy: str | None = proxy
        self.proxies: dict[str, str] | None = proxies
        self.mounts: dict[str, httpx.HTTPTransport] | None = mounts
        self.auth: httpx.Auth | None = auth
        self.headers: dict[str, str] | None = headers
        self.cookies: dict[str, t.Any] | None = cookies
        self.params: dict[str, str] | None = params
        self.follow_redirects: bool = follow_redirects
        self.max_redirects: int | None = max_redirects
        self.timeout: t.Union[int, float] | None = timeout
        self.limits: httpx.Limits | None = limits
        self.transport: httpx.HTTPTransport | hishel.CacheTransport | None = transport
        self.default_encoding: str = default_encoding

        ## Placeholder for initialized httpx.Client
        self.client: httpx.Client | None = None

    def __enter__(self):
        try:
            _client: httpx.Client = httpx.Client(
                auth=self.auth,
                params=self.params,
                headers=self.headers,
                cookies=self.cookies,
                proxy=self.proxy,
                proxies=self.proxies,
                mounts=self.mounts,
                timeout=self.timeout,
                follow_redirects=self.follow_redirects,
                max_redirects=self.max_redirects,
                # base_url=self.base_url,
                transport=self.transport,
                default_encoding=self.default_encoding,
            )

            if self.base_url:
                _client.base_url = self.base_url

            self.client = _client

            return self

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception initializing httpx Client. Details: {exc}"
            )
            log.error(msg)

            raise exc

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            log.error(f"({exc_type}): {exc_value}")

        if traceback:
            log.trace(traceback)

        ## Close httpx client
        if self.client:
            self.client.close()

    def send_request(
        self,
        request: httpx.Request = None,
        stream: bool = False,
        auth: httpx.Auth = None,
    ) -> httpx.Response:
        assert request, ValueError("Missing an httpx.Request object")
        assert isinstance(request, httpx.Request), TypeError(
            f"Expected request to be an httpx.Request object. Got type: ({type(request)})"
        )

        try:
            res: httpx.Response = self.client.send(
                request=request,
                stream=stream,
                auth=auth,
                follow_redirects=self.follow_redirects,
            )
            log.debug(
                f"URL: {request.url}, Response: [{res.status_code}: {res.reason_phrase}]"
            )

            return res
        except httpx.ConnectError as conn_err:
            msg = Exception(
                f"ConnectError while requesting URL {request.url}. Details: {conn_err}"
            )
            log.error(msg)

            return
        except Exception as exc:
            msg = Exception(f"Unhandled exception sending request. Details: {exc}")
            log.error(msg)

            raise msg
