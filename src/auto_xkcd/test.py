from __future__ import annotations

from pathlib import Path
import random
import typing as t

from core import database
from core.dependencies import CACHE_TRANSPORT, db_settings, get_db, settings
from core.paths import DATA_DIR, ENSURE_DIRS, SERIALIZE_DIR
from core.request_client import HTTPXController, get_cache_transport
import hishel
import httpx
from loguru import logger as log
from modules import data_ctl, setup, xkcd_mod
import msgpack
from packages import xkcd
from packages.xkcd.comic.img import save_img
import pendulum
from pipelines import comic_pipelines
from red_utils.ext import time_utils
from red_utils.ext.loguru_utils import init_logger, sinks
from red_utils.std import path_utils
from utils import serialize_utils


def main(cache_transport: hishel.CacheTransport = None):
    current_comic: xkcd_mod.XKCDComic = comic_pipelines.pipeline_get_current_comic(
        cache_transport=cache_transport
    )
    # log.debug(f"Current comic ({type(current_comic)}): {current_comic}")
    current_img_saved: bool = save_img(
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


if __name__ == "__main__":
    init_logger(
        sinks=[
            sinks.LoguruSinkStdOut(level=settings.log_level).as_dict(),
            sinks.LoguruSinkAppFile(sink=f"{settings.logs_dir}/app.log").as_dict(),
            sinks.LoguruSinkErrFile(sink=f"{settings.logs_dir}/err.log").as_dict(),
        ]
    )

    log.info(f"Start auto-xkcd")

    setup._setup()

    cache_transport: hishel.CacheTransport = get_cache_transport(retries=3)

    main(cache_transport=cache_transport)
