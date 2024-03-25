from __future__ import annotations

from pathlib import Path
import random
import typing as t

from core import database, request_client
from core.config import db_settings, settings
from core.dependencies import get_db
from core.paths import ENSURE_DIRS, SERIALIZE_DIR
import httpx
from loguru import logger as log
from modules import xkcd_mod
from pipelines import (
    pipeline_current_comic,
    pipeline_random_comic,
    pipeline_specific_comic,
    pipeline_multiple_comics,
    pipeline_retrieve_missing_imgs,
)

import msgpack
from packages import xkcd
from red_utils.ext.loguru_utils import init_logger, sinks
from red_utils.std import path_utils
from utils import serialize_utils


def main():
    SPECIFIC_COMIC_NUM: int = 42
    MULTI_REQUEST_COMIC_NUMS: list[int] = [1, 15, 35, 71, 84]

    # current_comic_res: xkcd_mod.XKCDComic = pipeline_current_comic()
    # log.info(f"Current comic: {current_comic_res}")

    # random_comic_res: xkcd_mod.XKCDComic = pipeline_random_comic()
    # log.info(f"Random comic res: {random_comic_res}")

    # specific_comic: xkcd_mod.XKCDComic = pipeline_specific_comic(
    #     comic_num=SPECIFIC_COMIC_NUM
    # )
    # log.info(f"Comic #{SPECIFIC_COMIC_NUM}: {specific_comic}")

    # multiple_comics: list[xkcd_mod.XKCDComic] = pipeline_multiple_comics(
    #     comic_nums_list=MULTI_REQUEST_COMIC_NUMS
    # )
    # log.debug(f"Printing [{len(multiple_comics)}] comic(s) from multi-comic request")
    # for c in multiple_comics:
    #     log.debug(f"Comic #{c.comic_num}: {c}")

    retrieved_imgs = pipeline_retrieve_missing_imgs()


if __name__ == "__main__":
    settings.log_level = "DEBUG"

    init_logger(sinks=[sinks.LoguruSinkStdOut(level=settings.log_level).as_dict()])

    log.info(f"Start auto-xkcd")

    path_utils.ensure_dirs_exist(ensure_dirs=ENSURE_DIRS)

    main()
