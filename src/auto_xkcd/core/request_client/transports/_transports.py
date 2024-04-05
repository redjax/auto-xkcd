import typing as t
from loguru import logger as log
import hishel
import httpx


def get_cache_transport(
    cache_dir: str = ".cache/hishel",
    ttl: int | None = None,
    verify: bool = True,
    retries: int = 0,
    cert: t.Union[
        str, tuple[str, str | None], tuple[str, str | None, str | None]
    ] = None,
) -> hishel.CacheTransport:
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
