from __future__ import annotations

from pathlib import Path
import typing as t

from core.paths import DATA_DIR, SERIALIZE_DIR
import hishel
import httpx
from loguru import logger as log
from modules import data_ctl, xkcd_mod
import msgpack
from packages import xkcd
from packages.xkcd.comic import read_current_comic_meta
import pendulum
from utils import serialize_utils


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
            current_meta: xkcd_mod.CurrentComicMeta = xkcd_mod.CurrentComicMeta(
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

    _current_meta: xkcd_mod.CurrentComicMeta = read_current_comic_meta()
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
    comic_nums: list[int] = None,
    cache_transport: hishel.CacheTransport = None,
    request_sleep: int = 5,
) -> list[xkcd_mod.XKCDComic]:

    # if len(comic_nums) > 50:
    #     log.warning(f"Large list of comics detected. Breaking into smaller chunks.")

    deserialized_comics: list[xkcd_mod.XKCDComic] = []
    for num in comic_nums:
        serialized_res_path: Path = Path(
            f"{SERIALIZE_DIR}/comic_responses/{num}.msgpack"
        )

        # log.debug(f"Searching for serialized response: {serialized_res_path}")
        if serialized_res_path.exists():
            ## Found serialized response

            log.success(
                f"Comic #{num} found in serialized responses. Loading from file '{serialized_res_path}'"
            )
            try:
                with open(serialized_res_path, "rb") as f:
                    _content = msgpack.unpackb(f.read())

            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception loading serialized response from file '{serialized_res_path}'. Details: {exc}"
                )
                log.error(msg)
                log.trace(exc)

                raise exc

            log.debug(f"Removing comic #{num} from comic_nums: {comic_nums}")
            try:
                _comic: xkcd_mod.XKCDComic = xkcd_mod.XKCDComic.model_validate(_content)
                deserialized_comics.append(_comic)

                # comic_nums.remove(num)

            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception loading deserialized data into XKCDComic object. Details: {exc}"
                )
                log.error(msg)
                log.trace(exc)

                raise exc

        else:
            ## Did not find serialized response

            ## Suppress log output for large lists of comic numbers. Keeps from cluttering up the logs
            if len(comic_nums) < 20:
                log.warning(f"Did not find serialized response for comic #{num}")
            continue

    if deserialized_comics:
        log.debug(
            f"Loaded [{len(deserialized_comics)}] comic(s) from existing serialized response(s)"
        )

        found_comic_nums: list[int] = [c.num for c in deserialized_comics]
        log.debug(f"Removing comic nums from search list: {found_comic_nums}")

        for n in found_comic_nums:
            if n in comic_nums:
                comic_nums.remove(n)

    if len(comic_nums) == 0:
        log.info(f"All comics have already been downloaded.")

        return deserialized_comics

    # log.debug(f"Comic nums: {comic_nums}")

    comics: list[xkcd_mod.XKCDComic] = xkcd.comic.get_multiple_comics(
        comic_nums=comic_nums,
        cache_transport=cache_transport,
        request_sleep=request_sleep,
    )
    log.info(f"Requested [{len(comics)}] comic(s)")

    if deserialized_comics:
        log.debug(f"Joining deserialized responses with live responses")
        comics_join = comics + deserialized_comics
        comics = comics_join

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


def _list_missing_comic_imgs(current_comic_num: int = None):
    with data_ctl.SavedImgsController() as imgs_ctl:
        saved_comic_nums: list[int] = imgs_ctl.comic_nums

    missing_comic_nums: list[int] = []
    for i in range(1, current_comic_num):
        if i not in saved_comic_nums:
            missing_comic_nums.append(i)

    return missing_comic_nums
