from __future__ import annotations

from pathlib import Path
import random
import typing as t

from core import database
from core.request_client import HTTPXController
from core.dependencies import db_settings, get_db, settings
from core.paths import ENSURE_DIRS, SERIALIZE_DIR
import httpx
import hishel
from loguru import logger as log

from red_utils.ext.loguru_utils import init_logger, sinks
from red_utils.std import path_utils

from utils import serialize_utils


def _setup() -> None:
    log.info("Analyzing existing data...")

    try:
        path_utils.ensure_dirs_exist(ensure_dirs=ENSURE_DIRS)
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception creating initial directories. Details: {exc}"
        )
        log.error(msg)

        raise exc

    # try:
    #     xkcd.helpers.update_comic_num_img_bool()
    # except Exception as exc:
    #     msg = Exception(
    #         f"Unhandled exception synching saved comic data. Continuing as-is (this will be updated throughout pipelines, it's ok to skip)."
    #     )
    #     log.error(msg)

    #     return


def main():
    XKCD_BASE_URL: str = "https://xkcd.com"
    CURRENT_COMIC_ENDPOINT: str = "/info.0.json"
    CURRENT_COMIC_URL: str = f"{XKCD_BASE_URL}/{CURRENT_COMIC_ENDPOINT}"

    # Create a cache instance with hishel
    cache_storage = hishel.FileStorage(base_path=".cache/hishel", ttl=None)
    cache_transport = httpx.HTTPTransport(verify=True, cert=None)
    # Create an HTTP cache transport
    cache_transport = hishel.CacheTransport(
        transport=cache_transport, storage=cache_storage
    )

    # Create an HTTPX client with the cache transport
    client = httpx.Client(transport=cache_transport)

    with HTTPXController(transport=cache_transport) as httpx_ctl:

        req: httpx.Request = httpx_ctl.new_request(url=CURRENT_COMIC_URL)
        transport: hishel.CacheTransport = httpx_ctl.get_cache_transport(retries=3)
        httpx_ctl.transport = transport

        res: httpx.Response = httpx_ctl.send_request(request=req)
        log.debug(f"Response: [{res.status_code}: {res.reason_phrase}]")


if __name__ == "__main__":
    init_logger(
        sinks=[
            sinks.LoguruSinkStdOut(level=settings.log_level).as_dict(),
            sinks.LoguruSinkAppFile(sink=f"{settings.logs_dir}/app.log").as_dict(),
            sinks.LoguruSinkErrFile(sink=f"{settings.logs_dir}/err.log").as_dict(),
        ]
    )

    log.info(f"Start auto-xkcd")

    _setup()

    main()
