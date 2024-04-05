from __future__ import annotations

from pathlib import Path
import random
import typing as t

from core import database
from core.request_client import HTTPXController, get_cache_transport
from core.dependencies import db_settings, get_db, settings, CACHE_TRANSPORT
from core.paths import ENSURE_DIRS, SERIALIZE_DIR, DATA_DIR
import httpx
import hishel
from loguru import logger as log

from red_utils.ext.loguru_utils import init_logger, sinks
from red_utils.std import path_utils

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


def _get_current(cache_transport: hishel.CacheTransport = None) -> xkcd_mod.XKCDComic:
    current_comic: xkcd_mod.XKCDComic = xkcd.comic.get_current_comic(
        cache_transport=cache_transport
    )
    log.info(f"Current comic: {current_comic}")

    ## Serialize comic to msgpack file
    serialize_utils.serialize_dict(
        data=current_comic.model_dump(),
        output_dir=f"{SERIALIZE_DIR}/comic_responses",
        filename=f"{current_comic.comic_num}.msgpack",
    )

    # update_comic_nums_file(comic_num=current_comic.comic_num)

    return current_comic


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
            filename=f"{c.comic_num}.msgpack",
        )

        # update_comic_nums_file(comic_num=c.comic_num)

    return comics


def main(cache_transport: hishel.CacheTransport = None):
    current_comic: xkcd_mod.XKCDComic = _get_current(cache_transport=cache_transport)

    # comics: list[xkcd_mod.XKCDComic] = _get_multiple(
    #     comic_nums=[1, 15, 64, 83, 125, 65], cache_transport=cache_transport
    # )

    # scraped_comics = xkcd.comic.scraper.start_scrape(cache_transport=cache_transport)

    img_test = xkcd.comic.img.save_img(
        comic=current_comic, output_filename=f"{current_comic.comic_num}.png"
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

    _setup()

    cache_transport = get_cache_transport(retries=3)

    main(cache_transport=cache_transport)
