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

def demo_current_comic() -> xkcd_mod.XKCDComic:
    current_comic_res: xkcd_mod.XKCDComic = pipeline_current_comic()
    log.info(f"Current comic: {current_comic_res}")

    return current_comic_res


def demo_random_comic() -> xkcd_mod.XKCDComic:
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


def demo_update_img_saved_values() -> None:
    pipeline_update_img_saved_vals()

    return


def demo_all(
    req_sleep: int = 5,
    specific_comic_num: int = 42,
    multi_request_comic_ums: list[int] = [1, 15, 35, 71, 84],
):

    log.info("Updating img_saved bool column in CSV file.")
    _update_csv = xkcd.helpers.update_comic_num_img_bool()

    _current_comic: xkcd_mod.XKCDComic = demo_current_comic()
    _random_comic: xkcd_mod.XKCDComic = demo_random_comic()
    _specific_comic: xkcd_mod.XKCDComic = demo_specific_comic(
        comic_num=specific_comic_num
    )
    _prepared_multi_comic: list[xkcd_mod.XKCDComic] = demo_prepared_muliple_comics(
        comic_nums=multi_request_comic_ums
    )

    with xkcd.helpers.ComicNumsController() as comicnum_ctl:
        most_recent_comic = comicnum_ctl.max_comic_num()

    ALL_COMIC_NUMS: list[int] = [n for n in range(1, most_recent_comic)]

    _all_comics: list[xkcd_mod.XKCDComic] = demo_req_all_comics(
        all_comic_nums=ALL_COMIC_NUMS
    )

    _missing_imgs: None = demo_req_missing_imgs()

    _update_img_saved = demo_update_img_saved_values()


if __name__ == "__main__":
    settings.log_level = "DEBUG"
    init_logger(sinks=[sinks.LoguruSinkStdOut(level=settings.log_level).as_dict()])

    log.info(f"[DEMO] Start auto-xkcd")

    path_utils.ensure_dirs_exist(ensure_dirs=ENSURE_DIRS)

    demo_all()
