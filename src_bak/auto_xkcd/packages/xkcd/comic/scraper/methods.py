from __future__ import annotations

import typing as t

import hishel
import httpx
from loguru import logger as log
from modules import data_ctl, xkcd_mod
from packages.xkcd.comic.methods import (
    get_current_comic,
    get_multiple_comics,
    request_comic,
)

def list_missing_comic_imgs(current_comic_num: int = None):
    with data_ctl.SavedImgsController() as imgs_ctl:
        saved_comic_nums: list[int] = imgs_ctl.comic_nums

    missing_comic_nums: list[int] = []
    for i in range(1, current_comic_num):
        if i not in saved_comic_nums:
            missing_comic_nums.append(i)

    return missing_comic_nums


def start_scrape(cache_transport: hishel.CacheTransport = None):
    log.info(f"Getting current XKCD comic number")
    current_comic: xkcd_mod.XKCDComic = get_current_comic(
        cache_transport=cache_transport
    )
    log.debug(f"Current XKCD comic: #{current_comic.num}")

    missing_comic_imgs: list[int] = list_missing_comic_imgs(
        current_comic_num=current_comic.num
    )
    if not missing_comic_imgs:
        log.warning(
            f"Did not find any missing comic images. Either an error occurred, or all comic images have been downloaded."
        )
    if len(missing_comic_imgs) > 1:
        log.debug(f"Scraping [{len(missing_comic_imgs)}] missing comic(s)")
    else:
        log.debug(f"Scraping 1 comic: {missing_comic_imgs[0]}")

    for missing_img in missing_comic_imgs:
        # log.debug(f"Scraping comic #{missing_img}")
        pass
