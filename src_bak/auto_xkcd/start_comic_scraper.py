from __future__ import annotations

from core import database
from core.dependencies import CACHE_TRANSPORT, db_settings, get_db, settings
from core.paths import DATA_DIR, ENSURE_DIRS, SERIALIZE_DIR
from core.request_client import HTTPXController, get_cache_transport
import hishel
import httpx
from loguru import logger as log
from modules import data_ctl, xkcd_mod
from modules.setup import _setup
import msgpack
from packages import xkcd
import pendulum
from pipelines import comic_pipelines
from red_utils.ext import time_utils
from red_utils.ext.loguru_utils import init_logger, sinks
from red_utils.std import path_utils
from utils import serialize_utils

def main(cache_transport: hishel.CacheTransport = None, request_sleep: int = 5):
    log.info("Scraping missing comics.")
    try:
        scraped_comics: list[xkcd_mod.XKCDComic] | None = (
            comic_pipelines.pipeline_scrape_missing_comics(
                cache_transport=cache_transport, request_sleep=request_sleep
            )
        )
    except Exception as exc:
        msg = Exception(f"Unhandled exception scraping comics. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc

    return scraped_comics


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

    scraped_comics: list[xkcd_mod.XKCDComic] | None = main(
        cache_transport=cache_transport
    )
    if scraped_comics is None or len(scraped_comics) == 0:
        log.info("Did not find any missing comics. Have all comics been downloaded?")
    else:
        log.info(f"Scraped [{len(scraped_comics)}] comic(s)")
