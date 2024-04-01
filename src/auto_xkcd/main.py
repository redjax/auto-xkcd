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
)
from red_utils.ext.loguru_utils import init_logger, sinks
from red_utils.std import path_utils
from utils import serialize_utils


def demo_current_comic(req_sleept: int = 5) -> xkcd_mod.XKCDComic:
    current_comic_res: xkcd_mod.XKCDComic = pipeline_current_comic()
    log.info(f"Current comic: {current_comic_res}")

    return current_comic_res


def demo_random_comic(req_sleept: int = 5) -> xkcd_mod.XKCDComic:
    random_comic_res: xkcd_mod.XKCDComic = pipeline_random_comic()
    log.info(f"Random comic res: {random_comic_res}")

    return random_comic_res


def demo_specific_comic(comic_num: int = None) -> xkcd_mod.XKCDComic:
    specific_comic: xkcd_mod.XKCDComic = pipeline_specific_comic(comic_num=comic_num)
    log.info(f"Comic #{comic_num}: {specific_comic}")

    return specific_comic


def demo_prepared_muliple_comics(
    comic_nums: list[int] = None, req_sleep: int = 5
) -> list[xkcd_mod.XKCDComic]:
    multiple_comics: list[xkcd_mod.XKCDComic] = pipeline_multiple_comics(
        comic_nums_list=comic_nums, request_sleep=req_sleep
    )
    log.debug(f"Printing [{len(multiple_comics)}] comic(s) from multi-comic request")
    for c in multiple_comics:
        log.debug(f"Comic #{c.comic_num}: {c}")

    return multiple_comics


def demo_req_all_comics(
    all_comic_nums: list[int] = None, req_sleep: int = 5
) -> list[xkcd_mod.XKCDComic]:
    multiple_comics: list[xkcd_mod.XKCDComic] = pipeline_multiple_comics(
        comic_nums_list=all_comic_nums, request_sleep=req_sleep
    )

    return multiple_comics


def demo_req_missing_imgs(req_sleep: int = 5) -> None:
    retrieved_imgs: None = pipeline_retrieve_missing_imgs(request_sleep=req_sleep)

    return retrieved_imgs


def main(req_sleep: int = 5):
    SPECIFIC_COMIC_NUM: int = 42
    MULTI_REQUEST_COMIC_NUMS: list[int] = [1, 15, 35, 71, 84]

    ALL_COMIC_NUMS: list[int] = [n for n in range(1, 2913)]

    _current_comic: xkcd_mod.XKCDComic = demo_current_comic()
    _random_comic: xkcd_mod.XKCDComic = demo_random_comic()
    _specific_comic: xkcd_mod.XKCDComic = demo_specific_comic(
        comic_num=SPECIFIC_COMIC_NUM
    )
    _prepared_multi_comic: list[xkcd_mod.XKCDComic] = demo_prepared_muliple_comics(
        comic_nums=MULTI_REQUEST_COMIC_NUMS
    )
    _all_comics: list[xkcd_mod.XKCDComic] = demo_req_all_comics(
        all_comic_nums=ALL_COMIC_NUMS
    )

    _missing_imgs: None = demo_req_missing_imgs()


if __name__ == "__main__":
    settings.log_level = "DEBUG"

    init_logger(sinks=[sinks.LoguruSinkStdOut(level=settings.log_level).as_dict()])

    log.info(f"Start auto-xkcd")

    path_utils.ensure_dirs_exist(ensure_dirs=ENSURE_DIRS)

    main()
