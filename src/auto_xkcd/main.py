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
import msgpack
from packages import xkcd
from red_utils.ext.loguru_utils import init_logger, sinks
from red_utils.std import path_utils
from utils import serialize_utils


def _current(save_serial: bool = True) -> dict:
    try:
        current_comic_res: httpx.Response = xkcd.request_current_comic()
        url_hash: str = xkcd.helpers.url_hash(url=current_comic_res.url)
        log.debug(f"URL hash: {url_hash}")

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting current XKCD comic. Details: {exc}"
        )

        raise msg

    try:
        current_comic_dict: dict = xkcd.helpers.parse_comic_response(
            res=current_comic_res
        )
        comic_hash: str = xkcd.helpers.comic_num_hash(
            comic_num=current_comic_dict["num"]
        )
        log.debug(f"Comic num [{current_comic_dict['num']}] hash: {comic_hash}")

        ## Append hashes to response dict
        current_comic_dict["url_hash"] = url_hash

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception parsing current XKCD comic response. Details: {exc}"
        )
        log.error(msg)

        raise msg

    if save_serial:
        serial_filename: str = str(current_comic_dict["num"]) + ".msgpack"

        try:
            log.debug(f"Serialized filename: {serial_filename}")
            xkcd.helpers.serialize_response(
                res=current_comic_res, filename=serial_filename
            )
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception serializing comic response. Details: {exc}"
            )
            log.error(msg)

    return current_comic_dict


def max_comic_num() -> int:
    with xkcd.helpers.ComicNumsController() as comic_nums:
        current_comic_num = comic_nums.highest()
        log.info(f"Highest comic number recorded: {current_comic_num}")

    return current_comic_num


def main():
    current_comic_res: dict = _current()
    log.debug(f"Current comic response: {current_comic_res}")

    current_comic: xkcd_mod.XKCDComic = xkcd_mod.XKCDComic().model_validate(
        current_comic_res
    )
    log.info(f"Current comic: {current_comic}")

    with xkcd.helpers.ComicNumsController() as comic_nums:
        data = xkcd_mod.ComicNumCSVData(
            comic_num=current_comic.comic_num, img_saved=False
        )

        comic_nums.add_comic_num_data(data.model_dump())

    random_comic_res: dict = xkcd.get_random_comic()
    log.debug(f"Random comic response: {random_comic_res}")

    random_comic: xkcd_mod.XKCDComic = xkcd_mod.XKCDComic().model_validate(
        random_comic_res
    )
    log.info(f"Random comic: {random_comic}")

    with xkcd.helpers.ComicNumsController() as comic_nums:
        random_comic_data = xkcd_mod.ComicNumCSVData(
            comic_num=random_comic.comic_num, img_saved=False
        )
        comic_nums.add_comic_num_data(random_comic_data.model_dump())


if __name__ == "__main__":
    settings.log_level = "DEBUG"

    init_logger(sinks=[sinks.LoguruSinkStdOut(level=settings.log_level).as_dict()])

    log.info(f"Start auto-xkcd")
    log.debug(f"Settings: {settings}")
    log.debug(f"DB settings: {db_settings}")

    path_utils.ensure_dirs_exist(ensure_dirs=ENSURE_DIRS)

    main()
