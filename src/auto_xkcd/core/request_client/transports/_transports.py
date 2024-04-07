from __future__ import annotations

import typing as t

import hishel
import httpx
from loguru import logger as log


def get_cache_transport(
    cache_dir: str = ".cache/hishel",
    ttl: int | None = None,
    verify: bool = True,
    retries: int = 0,
    cert: t.Union[
        str, tuple[str, str | None], tuple[str, str | None, str | None]
    ] = None,
) -> hishel.CacheTransport:
    """Return an initialized hishel.CacheTransport.

    Params:
        cache_dir (str): [default: .cache/hishel] Directory where cache files will be stored.
        ttl (int|None): [default: None] Limit ttl on requests sent with this transport.
        verify (bool): [default: True] Verify SSL certificates on requests sent with this transport.
        retriest (int): [default: 0] Number of times to retry requests sent with this transport.
        cert (valid HTTPX Cert): An optional SSL certificate to send with requests.

    """
    # Create a cache instance with hishel
    cache_storage = hishel.FileStorage(base_path=cache_dir, ttl=ttl)
    cache_transport = httpx.HTTPTransport(verify=verify, cert=cert, retries=retries)

    try:
        # Create an HTTP cache transport
        cache_transport = hishel.CacheTransport(
            transport=cache_transport, storage=cache_storage
        )

        return cache_transport
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception returning cache transport. Details: {exc}"
        )
        log.error(msg)

        raise exc
