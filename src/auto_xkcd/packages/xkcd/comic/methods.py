import typing as t
from core.request_client import HTTPXController
from modules import xkcd_mod

from loguru import logger as log

import hishel
import httpx


def get_current_comic() -> None | xkcd_mod.XKCDComic:
    with HTTPXController() as httpx_ctl:
        transport: hishel.CacheTransport = httpx_ctl.get_cache_transport(retries=3)
        httpx_ctl.transport = transport

        req: httpx.Request = httpx_ctl.new_request(url=xkcd_mod.CURRENT_XKCD_URL)

        try:
            comic_res: httpx.Response = httpx_ctl.send_request(request=req)

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception getting current XKCD comic. Details: {exc}"
            )
            log.error(msg)

            raise exc

        if not comic_res.status_code == 200:
            log.warning(
                f"Non-200 response: [{comic_res.status_code}: {comic_res.reason_phrase}]: {comic_res.text}"
            )
            return

        log.debug(f"Converting current comic Response to dict")
        try:
            comic_dict = httpx_ctl.decode_res_content(res=comic_res)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception decoding current comic response bytes. Details: {exc}"
            )
            log.error(msg)

            raise exc

        log.debug(f"Converting current comic dict to XKCDComic")
        try:
            comic = xkcd_mod.XKCDComic.model_validate(comic_dict)

            return comic
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception converting current comic dict to XKCDComic object. Details: {exc}"
            )
            log.error(msg)

            raise exc
