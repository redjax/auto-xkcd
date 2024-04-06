from __future__ import annotations

from pathlib import Path
import random
import typing as t

from core import database
from core.request_client import HTTPXController, get_cache_transport
from core.dependencies import db_settings, get_db, settings, CACHE_TRANSPORT
from core.paths import ENSURE_DIRS, SERIALIZE_DIR, DATA_DIR

from modules import data_ctl
import httpx
import hishel
import pendulum
from loguru import logger as log

from red_utils.ext.loguru_utils import init_logger, sinks
from red_utils.std import path_utils
from red_utils.ext import time_utils
import msgpack

from utils import serialize_utils

from modules import xkcd_mod
from packages import xkcd


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


def update_comic_nums_file(
    file: t.Union[str, Path] = f"{DATA_DIR}/comic_nums.txt", comic_num: int = None
):
    assert comic_num, ValueError("Missing comic number")
    assert isinstance(comic_num, int), TypeError(f"comic_num must be an integer")

    assert isinstance(file, str) or isinstance(file, Path), TypeError(
        f"file must be a string or Path object. Got type: ({type(file)})"
    )
    if isinstance(file, str):
        file: Path = Path(file)
    if "~" in f"{file}":
        file: Path = file.expanduser()

    if not file.parent.exists():
        try:
            file.parent.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception creating directory '{file.parent}'. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            raise exc

    if not file.exists():
        file.touch()

    with open(file, "r") as f:
        lines = f.readlines()
        comic_nums: list[int] = []
        for line in lines:
            stripped = int(line.strip())
            comic_nums.append(stripped)

    if comic_num not in comic_nums:
        log.debug(f"Comic num [{comic_num}] not in comic_nums: {comic_nums}")
        lines.append(comic_num)
        with open(file, "w") as f:
            for line in lines:
                f.write(f"{line}\n")


def _get_current(
    cache_transport: hishel.CacheTransport = None,
    force_live_request: bool = False,
    stale_years: int = 0,
    stale_months: int = 0,
    stale_weeks: int = 0,
    stale_days: int = 0,
    stale_hours: int = 6,
    stale_minutes: int = 0,
    stale_seconds: int = 0,
) -> xkcd_mod.XKCDComic:
    """Get the current XKCD comic.

    Checks the "current_comic.json" file for the most recently known current comic. If current_comic info
    is not stale (the stale_<time> params control staleness), the comic is loaded from its serialized version, if
    it exists.

    If a comic is stale, forces a live request & update of the current_comic.json file.

    Params:
        cache_transport (hishel.CacheTransport): The cache transport to send to any functions that make requests.
        force_lib_request (bool): If `True`, skip checking current_comic.json and force live request & update of current_comic.json.
        stale_years (int): Combin with other `stale_X` values to control staleness check. Uses the current_comic.json's 'last_updated' value to compare for staleness.
        stale_months (int): Combin with other `stale_X` values to control staleness check. Uses the current_comic.json's 'last_updated' value to compare for staleness.
        stale_weeks (int): Combin with other `stale_X` values to control staleness check. Uses the current_comic.json's 'last_updated' value to compare for staleness.
        stale_days (int): Combin with other `stale_X` values to control staleness check. Uses the current_comic.json's 'last_updated' value to compare for staleness.
        stale_hours (int): Combin with other `stale_X` values to control staleness check. Uses the current_comic.json's 'last_updated' value to compare for staleness.
        stale_minutes (int): Combin with other `stale_X` values to control staleness check. Uses the current_comic.json's 'last_updated' value to compare for staleness.
        stale_seconds (int): Combin with other `stale_X` values to control staleness check. Uses the current_comic.json's 'last_updated' value to compare for staleness.

    """

    def check_stale(last_updated_date: pendulum.DateTime = None):
        staleness_check: pendulum.DateTime = pendulum.now().subtract(
            years=stale_years,
            months=stale_months,
            weeks=stale_weeks,
            days=stale_days,
            hours=stale_hours,
            minutes=stale_minutes,
            seconds=stale_seconds,
        )

        if staleness_check > last_updated_date:
            return True
        else:
            return False

    output_dir: str = f"{SERIALIZE_DIR}/comic_responses"

    if force_live_request:
        log.warning(f"force_live_request=True, skipping check for existing comic data.")

        current_comic: xkcd_mod.XKCDComic = xkcd.comic.get_current_comic(
            cache_transport=cache_transport
        )
        log.info(f"Current comic: {current_comic}")

        filename = f"{current_comic.num}.msgpack"

        ## Serialize comic to msgpack file
        serialize_utils.serialize_dict(
            data=current_comic.model_dump(),
            output_dir=output_dir,
            filename=filename,
            overwrite=True,
        )

        try:
            current_meta = xkcd_mod.CurrentComicMeta = xkcd_mod.CurrentComicMeta(
                comic_num=current_comic.num, last_updated=pendulum.now()
            )
            log.debug(f"Current comic metadata: {current_meta}")
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception creating CurrentComicMeta object. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            raise exc

        try:
            xkcd.comic.update_current_comic_meta(current_comic=current_meta)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception updating current_comic_metadata file with metadata: {current_meta}. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            raise exc

        # current_comic.link = xkcd_mod.XKCD_URL_BASE

        return current_comic

    _current_meta: xkcd_mod.CurrentComicMeta = xkcd.comic.read_current_comic_meta()
    # log.debug(f"Current comic metadata: {_current_meta}")

    if _current_meta.comic_num is None:
        log.warning(f"Comic num is None, forcing live request to update comic number.")
        current_comic = _get_current(
            cache_transport=cache_transport,
            force_live_request=True,
            stale_years=stale_years,
            stale_months=stale_months,
            stale_weeks=stale_weeks,
            stale_days=stale_days,
            stale_hours=stale_hours,
            stale_minutes=stale_minutes,
            stale_seconds=stale_seconds,
        )
        # current_comic.link = xkcd_mod.XKCD_URL_BASE
        log.debug(f"Current comic ({type(current_comic)}): {current_comic}")

        return current_comic

    if check_stale(last_updated_date=_current_meta.last_updated):
        log.warning(f"Current metadata is stale. Refreshing.")
        current_comic: xkcd_mod.XKCDComic = _get_current(
            cache_transport=cache_transport,
            force_live_request=True,
            stale_years=stale_years,
            stale_months=stale_months,
            stale_weeks=stale_weeks,
            stale_days=stale_days,
            stale_hours=stale_hours,
            stale_minutes=stale_minutes,
            stale_seconds=stale_seconds,
        )
        # current_comic.link = xkcd_mod.XKCD_URL_BASE

        return current_comic

    log.info(
        f"Current comic #{_current_meta.comic_num} was last updated [{_current_meta.last_updated}]. Loading from serialized file."
    )

    filename = f"{_current_meta.comic_num}.msgpack"
    serialize_file_path = Path(f"{output_dir}/{filename}")
    # log.debug(
    #     f"Loading comic #{_current_meta.comic_num} from file '{serialize_file_path}'."
    # )

    try:
        with open(serialize_file_path, "rb") as f:
            _read_data = f.read()
            data = msgpack.unpackb(_read_data)
            # log.debug(f"Loaded serialized data ({type(data)}): {data}")

    except FileNotFoundError as fnf:
        msg = Exception(
            f"Could not find serialized comic file at path '{serialize_file_path}'. Forcing live request."
        )
        log.warning(msg)

        current_comic: xkcd_mod.XKCDComic = _get_current(
            cache_transport=cache_transport,
            force_live_request=True,
            stale_years=stale_years,
            stale_months=stale_months,
            stale_weeks=stale_weeks,
            stale_days=stale_days,
            stale_hours=stale_hours,
            stale_minutes=stale_minutes,
            stale_seconds=stale_seconds,
        )

        return current_comic

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception loading comic #{_current_meta.comic_num} serialized data from file '{serialize_file_path}'. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    try:
        # log.debug(f"Comic response data ({type(data)}): {data}")
        current_comic: xkcd_mod.XKCDComic = xkcd_mod.XKCDComic.model_validate(data)
        # log.debug(f"Current comic object ({type(current_comic)}): {current_comic}")

        return current_comic
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception converting serialized data in file '{serialize_file_path}' to XKCDComic object. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc


def _get_multiple(
    comic_nums: list[int] = None, cache_transport: hishel.CacheTransport = None
) -> list[xkcd_mod.XKCDComic]:
    comics: list[xkcd_mod.XKCDComic] = xkcd.comic.get_multiple_comics(
        comic_nums=comic_nums, cache_transport=cache_transport
    )
    log.info(f"Requested [{len(comics)}] comic(s)")

    for c in comics:
        log.debug(f"Comic: {c}")

        ## Serialize comic to msgpack file
        serialize_utils.serialize_dict(
            data=c.model_dump(),
            output_dir=f"{SERIALIZE_DIR}/comic_responses",
            filename=f"{c.num}.msgpack",
        )

        # update_comic_nums_file(comic_num=c.num)

    return comics


def main(cache_transport: hishel.CacheTransport = None):
    current_comic: xkcd_mod.XKCDComic = _get_current(cache_transport=cache_transport)
    # log.debug(f"Current comic ({type(current_comic)}): {current_comic}")
    current_img_saved: bool = xkcd.comic.img.save_img(
        comic=current_comic, output_filename=f"{current_comic.num}.png"
    )
    # log.debug(f"Image saved ({type(current_img_saved)}): {current_img_saved}")

    comics: list[xkcd_mod.XKCDComic] = _get_multiple(
        comic_nums=[1, 15, 64, 83, 125, 65], cache_transport=cache_transport
    )
    saved_comics: list[xkcd_mod.XKCDComic] = []
    for c in comics:
        comic_saved = xkcd.comic.img.save_img(comic=c, output_filename=f"{c.num}.png")
        if comic_saved:
            saved_comics.append(c)

    with data_ctl.SavedImgsController() as savedimgs_ctl:
        log.debug(f"Found images for comic numbers: {savedimgs_ctl.comic_nums}")
        # log.debug(f"Images: {savedimgs_ctl.comic_imgs}")

    # scraped_comics = xkcd.comic.scraper.start_scrape(cache_transport=cache_transport)

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

    cache_transport = get_cache_transport(retries=3)

    # with open(f"{SERIALIZE_DIR}/comic_responses/2916.msgpack", "rb") as f:
    #     data = f.read()
    #     test = msgpack.unpackb(data)
    #     log.debug(f"Comic 2916 deserialized ({type(test)}): {test}")

    #     input("PAUSE...")

    main(cache_transport=cache_transport)
