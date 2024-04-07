from __future__ import annotations

from pathlib import Path
import random
import typing as t

from core import database
from core.request_client import HTTPXController, get_cache_transport
from core.dependencies import db_settings, get_db, settings, CACHE_TRANSPORT
from core.paths import ENSURE_DIRS, SERIALIZE_DIR, DATA_DIR

from modules import data_ctl
from utils import serialize_utils
from modules import xkcd_mod
from packages import xkcd
from pipelines import comic_pipelines

import httpx
import hishel
import pendulum
from loguru import logger as log

from red_utils.ext.loguru_utils import init_logger, sinks
from red_utils.std import path_utils
from red_utils.ext import time_utils
import msgpack


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


def main(cache_transport: hishel.CacheTransport = None):
    current_comic: xkcd_mod.XKCDComic = comic_pipelines.pipeline_get_current_comic(
        cache_transport=cache_transport
    )
    # log.debug(f"Current comic ({type(current_comic)}): {current_comic}")
    current_img_saved: bool = xkcd.comic.img.save_img(
        comic=current_comic, output_filename=f"{current_comic.num}.png"
    )
    # log.debug(f"Image saved ({type(current_img_saved)}): {current_img_saved}")

    comics: list[xkcd_mod.XKCDComic] = comic_pipelines.pipeline_get_multiple_comics(
        cache_transport=cache_transport,
        comic_nums=[1, 15, 64, 83, 125, 65],
        request_sleep=5,
    )

    scraped_comics = comic_pipelines.pipeline_scrape_missing_comics(
        cache_transport=cache_transport, request_sleep=5
    )

    _current_meta: xkcd_mod.CurrentComicMeta = xkcd.comic.read_current_comic_meta()
    # log.debug(f"Current comic metadata: {_current_meta}")


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

    cache_transport: hishel.CacheTransport = get_cache_transport(retries=3)

    main(cache_transport=cache_transport)
