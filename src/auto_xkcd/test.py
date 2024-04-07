from core.dependencies import settings
from core import request_client, XKCD_URL_POSTFIX, XKCD_URL_BASE, CURRENT_XKCD_URL
from _setup import base_app_setup

from loguru import logger as log

import httpx
import hishel


if __name__ == "__main__":
    base_app_setup(settings=settings)
    log.info(f"[TEST][env:{settings.env}|container:{settings.container_env}] App Start")

    current_comic_req: httpx.Request = request_client.build_request(
        url=CURRENT_XKCD_URL
    )
    CACHE_TRANSPORT: hishel.CacheTransport = request_client.get_cache_transport()

    try:
        with request_client.HTTPXController(transport=CACHE_TRANSPORT) as httpx_ctl:
            res = httpx_ctl.send_request(request=current_comic_req)
            log.debug(
                f"Current comic response: [{res.status_code}: {res.reason_phrase}]: {res.text}"
            )

    except Exception as exc:
        msg = Exception(f"Unhandled exception requesting current comic. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc
