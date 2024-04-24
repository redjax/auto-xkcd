import typing as t
import time

from .methods import existing_comics

from core.config import settings
from core.dependencies import get_db
from core import request_client
from modules import xkcd_mod
from packages import xkcd_comic
from domain.xkcd import comic
from modules.celery_mod.celeryapp import CELERY_APP
from red_utils.ext import msgpack_utils
from loguru import logger as log

import hishel
import httpx
import celery
import msgpack


def encode_comic(_comic: comic.XKCDComic = None):
    try:
        _dict = _comic.model_dump()
    except Exception as exc:
        msg = Exception(f"Unhandled exception dumping XKCDComic object. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise msg

    try:
        _packed = msgpack.packb(_dict)

        return _packed
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception packing XKCDComic into msgpack. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc


@CELERY_APP.task(name="get_current_comic")
def task_current_comic():
    CACHE_TRANSPORT: hishel.CacheTransport = request_client.get_cache_transport()

    try:
        current_comic: comic.XKCDComic = xkcd_comic.current_comic.get_current_comic(
            cache_transport=CACHE_TRANSPORT
        )

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting current XKCD comic. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    try:
        msg = encode_comic(current_comic)

        return msg
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception encoding XKCDComic for transit. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc
