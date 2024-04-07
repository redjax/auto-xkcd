from core.dependencies import settings
from core import request_client, XKCD_URL_POSTFIX, XKCD_URL_BASE, CURRENT_XKCD_URL
from _setup import base_app_setup
from modules import requests_prefab

from modules import xkcd_mod

from loguru import logger as log

import httpx
import hishel


def main(cache_transport: hishel.CacheTransport = None):
    assert cache_transport, ValueError(
        "Missing a cache transport for the request client"
    )
    assert isinstance(cache_transport, hishel.CacheTransport), TypeError(
        f"cache_transport must be a hishel.CacheTransport. Got type: ({type(cache_transport)})"
    )

    try:
        current_comic_req: httpx.Request = requests_prefab.current_comic_req()
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting current comic request prefab. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    try:
        with request_client.HTTPXController(transport=cache_transport) as httpx_ctl:
            res: httpx.Response = httpx_ctl.send_request(request=current_comic_req)
            log.debug(
                f"Current comic response: [{res.status_code}: {res.reason_phrase}]"
            )

            if not res.status_code == 200:
                log.warning(
                    f"Non-200 status code: [{res.status_code}: {res.reason_phrase}]: {res.text}"
                )

                raise NotImplementedError(
                    f"Error handling for non-200 status codes not yet implemented."
                )

        log.success(f"Current XKCD comic requested")

    except Exception as exc:
        msg = Exception(f"Unhandled exception requesting current comic. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc


if __name__ == "__main__":
    base_app_setup(settings=settings)
    log.info(f"[TEST][env:{settings.env}|container:{settings.container_env}] App Start")

    CACHE_TRANSPORT: hishel.CacheTransport = request_client.get_cache_transport()

    main(cache_transport=CACHE_TRANSPORT)
