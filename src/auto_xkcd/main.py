from __future__ import annotations

from pathlib import Path
import random
import typing as t

from core import database, request_client
from core.dependencies import db_settings, get_db, settings
from core.paths import ENSURE_DIRS, SERIALIZE_DIR
import httpx
from loguru import logger as log
from modules import xkcd_mod
import msgpack
from packages import xkcd
from pipelines import (
    pipeline_current_comic,
    pipeline_multiple_comics,
    pipeline_random_comic,
    pipeline_retrieve_missing_imgs,
    pipeline_specific_comic,
    pipeline_update_img_saved_vals,
)
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

    try:
        xkcd.helpers.update_comic_num_img_bool()
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception synching saved comic data. Continuing as-is (this will be updated throughout pipelines, it's ok to skip)."
        )
        log.error(msg)

        return


def main() -> None:
    ## Update img_saved row of CSV data. Do this last
    log.info("Synching saved comic data...")
    pipeline_update_img_saved_vals()

    log.info("Getting current XKCD comic")
    current_comic: xkcd_mod.XKCDComic = pipeline_current_comic()
    log.info(
        f"""Current XKCD comic [{current_comic.month}-{current_comic.day}-{current_comic.year}]
Title: #{current_comic.comic_num} - {current_comic.title}
Link: {current_comic.link if current_comic.link else '<Invalid or null link>.' }
Comic Img: {current_comic.img_url}
Alt Text: {current_comic.alt_text}
"""
    )

    log.info("Searching missing images")
    missing_imgs: None = pipeline_retrieve_missing_imgs()

    with xkcd.helpers.ComicNumsController() as comicnums_ctl:
        ALL_COMIC_NUMS: list[int] = [n for n in range(1, comicnums_ctl.highest)]

    log.info("Searching for downloadable comics")
    dl_comics: list[xkcd_mod.XKCDComic] = pipeline_multiple_comics(
        comic_nums_list=ALL_COMIC_NUMS
    )

    if dl_comics:
        log.info(f"Downloaded [{len(dl_comics)}] comic(s)")


if __name__ == "__main__":
    init_logger(
        sinks=[
            sinks.LoguruSinkStdOut(level=settings.log_level).as_dict(),
            sinks.LoguruSinkAppFile(sink=f"{settings.logs_dir}/app.log").as_dict(),
            sinks.LoguruSinkStdErr(sink=f"{settings.logs_dir}/err.log").as_dict(),
        ]
    )

    log.info(f"Start auto-xkcd")

    _setup()

    main()
