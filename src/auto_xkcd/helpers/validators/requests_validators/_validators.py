import hishel
import httpx


def validate_hishel_cachetransport(
    cache_transport: hishel.CacheTransport = None,
) -> hishel.CacheTransport:
    """Return a validated `hishel.CacheTransport` object.

    Params:
        cache_transport (hishel.CacheTransport): A cache transport instance.

    Returns:
        (hishel.CacheTransport): A validated `hishel.CacheTransport` object.

    """
    assert cache_transport, ValueError("cache_transport cannot be None")
    assert isinstance(cache_transport, hishel.CacheTransport), TypeError(
        f"cache_transport must be a hishel.CacheTransport object. Got type: ({type(cache_transport)})"
    )

    return cache_transport
