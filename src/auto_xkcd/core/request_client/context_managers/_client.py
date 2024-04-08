from __future__ import annotations

from contextlib import AbstractContextManager, contextmanager
import json
from pathlib import Path
import typing as t

## For auto detecting response character set
import chardet
import hishel
import httpx
from loguru import logger as log


def autodetect_charset(content: bytes = None):
    """Attempt to automatically detect encoding from input bytestring."""
    try:
        ## Detect encoding from bytes
        _encoding: str | None = chardet.detect(byte_str=content).get("encoding")

        if not _encoding:
            ## Default to utf-8
            _encoding = "utf-8"

        return _encoding

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception auto-detecting character set for input bytestring. Details: {exc}"
        )
        log.error(msg)
        log.warning("Defaulting to utf-8")

        return "utf-8"


class HTTPXController(AbstractContextManager):
    """Handler for HTTPX client.

    Params:
        url (str|None): Scope the httpx client to a URL.
        base_url (str|None): A base URL will be prefixed to each request. I.e. if `base_url="https://example.com",
            and you want to request "https://example.com/endpoint," you can set the base URL and then request `/endpoint`.
        proxy (str|None): <Not yet documented>
        proxies (str|None): <Not yet documented>
        mounts (dict[str, httpx.HTTPTransport]|None): A dict of `httpx.HTTPTransport` objects.
        cookies (dict[str, Any]): <Not yet documented>
        auth (httpx.Auth | None): <Not yet documented>
        headers (dict[str, str]|None): Optional request headers to apply to all requests handled by controller instance.
        params (dict[str, Any]|None): Optional request params to apply to all requests handled by controller instance.
        follow_redirects (bool): [Default: False] Follow HTTP 302 redirects.
        max_redirects (int|None): [Default: 20] Maximum number of HTTP 302 redirects to follow.
        retries (int|None): Number of times to retry on request failure.
        timeout (int|float|None): Timeout (in seconds) until client gives up on request.
        limits (httpx.Limits | None): <Not yet documented>
        transport (httpx.HTTPTransport|hishel.CacheTransport|None): A transport to pass to class's `httpx.Client` object.
        default_encoding (str): [Default: utf-8] Set default encoding for all requests.

    """

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
        retries: int | None = None,
        timeout: t.Union[int, float] | None = 60,
        limits: httpx.Limits | None = None,
        transport: t.Union[httpx.HTTPTransport, hishel.CacheTransport] | None = None,
        default_encoding: str = autodetect_charset,
    ) -> None:
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
        self.retries: int | None = retries
        self.timeout: t.Union[int, float] | None = timeout
        self.limits: httpx.Limits | None = limits
        self.transport: t.Union[httpx.HTTPTransport, hishel.CacheTransport] | None = (
            transport
        )
        self.default_encoding: str = default_encoding

        ## Placeholder for initialized httpx.Client
        self.client: httpx.Client | None = None

    def __enter__(self) -> t.Self:
        """Execute when handler is called in a `with` statement.

        Description:
            Creates an `httpx.Client` object, using class parameters as options.
        """
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

            ## If base_url is None, an exception occurs. Set self.base_url
            #  only if base_url is not None.
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
        """Execute  when `with` statement ends.

        Description:
            Show any exceptions/tracebacks. Close `self.client` on exit.

        """
        if exc_type:
            log.error(f"({exc_type}): {exc_value}")

        if traceback:
            log.trace(traceback)

        ## Close httpx client
        if self.client:
            self.client.close()

    def new_request(
        self,
        method: str = "GET",
        url: str | httpx.URL = None,
        files: list | None = None,
        _json: t.Any | None = None,
        headers: dict | None = {},
        cookies: dict | None = None,
        timeout: int | float | None = None,
    ) -> httpx.Request:
        """Assemble a new httpx.Request object from parts.

        Params:
            method (str): [Default: "GET"] HTTP method for request.
            url (str|httpx.URL): URL to send request.
            files (list|None): List of files to send with request. Only works with certain HTTP methods,
                list `POST`.
            json (t.Any | None): JSON to append to request.
            headers (dict|None): Request headers.
            cookies (dict): <Not yet documented>
            timeout (int|float): Timeout (in seconds) before cancelling request.

        Returns:
            (httpx.Request): An initialized `httpx.Request` object.

        """
        assert method, ValueError("Missing a request method")
        assert isinstance(method, str), TypeError(
            f"method should be a string. Got type: ({type(method)})"
        )

        ## Ensure method is uppercase, i.e. 'get' -> 'GET'
        method: str = method.upper()

        assert url, ValueError("Missing a URL")
        assert isinstance(url, str) or isinstance(url, httpx.URL), TypeError(
            f"URL must be a string or httpx.URL. Got type: ({type(url)})"
        )
        if isinstance(url, str):
            ## Convert URL from string into httpx.URL object
            url: httpx.URL = httpx.URL(url=url)

        if timeout:
            assert (
                isinstance(timeout, int) or isinstance(timeout, float)
            ) and timeout > 0, TypeError(
                f"timeout must be a non-zero positive int or float. Got type: ({type(timeout)})"
            )

        ## Build httpx.Request object
        try:
            _req: httpx.Request = self.client.build_request(
                method=method,
                url=url,
                files=files,
                json=_json,
                headers=headers,
                cookies=cookies,
                timeout=timeout,
            )

            return _req

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception creaeting httpx.Request object. Details: {exc}"
            )
            log.error(msg)

            raise msg

    def send_request(
        self,
        request: httpx.Request = None,
        stream: bool = False,
        auth: httpx.Auth = None,
    ) -> httpx.Response:
        """Send httpx.Request using self.Client (and optional cache transport).

        Params:
            request (httpx.Request): An initialized `httpx.Request` object.
            stream (bool): When `True`, response bytes will be streamed. This can be useful for large file downloads.
            auth (httpx.Auth): <Not yet documented>

        Returns:
            (httpx.Response): An `httpx.Response` from the request.

        """
        assert request, ValueError("Missing an httpx.Request object")
        assert isinstance(request, httpx.Request), TypeError(
            f"Expected request to be an httpx.Request object. Got type: ({type(request)})"
        )

        ## Send request using class's httpx.Client
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
            ## Error connecting to remote
            msg = Exception(
                f"ConnectError while requesting URL {request.url}. Details: {conn_err}"
            )
            log.error(msg)

            return
        except Exception as exc:
            msg = Exception(f"Unhandled exception sending request. Details: {exc}")
            log.error(msg)

            raise msg

    def decode_res_content(self, res: httpx.Response = None) -> dict:
        """Use multiple methods to attempt to decode an `httpx.Response.content` bytestring.

        Params:
            res (httpx.Response): An `httpx.Response` object, with `.content` to be decoded.

        Returns:
            (dict): A `dict` from the `httpx.Response`'s `.content` param.

        """
        assert res, ValueError("Missing httpx Response object")
        assert isinstance(res, httpx.Response), TypeError(
            f"res must be of type httpx.Response. Got type: ({type(res)})"
        )

        _content: bytes = res.content
        assert _content, ValueError("Response content is empty")
        assert isinstance(_content, bytes), TypeError(
            f"Expected response.content to be a bytestring. Got type: ({type(_content)})"
        )

        ## Get content's encoding, or default to 'utf-8'
        try:
            decode_charset: str = autodetect_charset(content=_content)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception detecting response content's encoding. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)
            log.warning(f"Defaulting to 'utf-8'")

            decode_charset: str = "utf-8"

        ## Decode content
        try:
            _decode: str = res.content.decode(decode_charset)

        except Exception as exc:
            ## Decoding failed, retry with different encodings
            msg = Exception(
                f"[Attempt 1/2] Unhandled exception decoding response content. Details: {exc}"
            )
            log.warning(msg)

            if not res.encoding == "utf-8":
                ## Try decoding again, using response's .encoding param
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
                ## Decoding with utf-8 failed, attempt with ISO-8859-1
                #  https://en.wikipedia.org/wiki/ISO/IEC_8859-1
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

        ## Load decoded content into dict
        try:
            _json: dict = json.loads(_decode)

            return _json

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception loading decoded response content to dict. Details: {exc}"
            )

            raise msg
