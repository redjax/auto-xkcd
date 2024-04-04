from __future__ import annotations

from pathlib import Path
import random
import typing as t

from core import database
from core.request_client import HTTPXController
from core.dependencies import db_settings, get_db, settings
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
        for l in lines:
            stripped = int(l.strip())
            comic_nums.append(stripped)

    if comic_num not in comic_nums:
        log.debug(f"Comic num [{comic_num}] not in comic_nums: {comic_nums}")
        lines.append(comic_num)
        with open(file, "w") as f:
            for l in lines:
                f.write(f"{l}\n")


def main():
    XKCD_BASE_URL: str = "https://xkcd.com"
    CURRENT_COMIC_ENDPOINT: str = "/info.0.json"
    CURRENT_COMIC_URL: str = f"{XKCD_BASE_URL}/{CURRENT_COMIC_ENDPOINT}"

    # Create a cache instance with hishel
    CACHE_STORAGE = hishel.FileStorage(base_path=".cache/hishel", ttl=None)
    HTTP_TRANSPORT = httpx.HTTPTransport(verify=True, cert=None, retries=3)
    # Create an HTTP cache transport
    CACHE_TRANSPORT = hishel.CacheTransport(
        transport=HTTP_TRANSPORT, storage=CACHE_STORAGE
    )

    current_comic: xkcd_mod.XKCDComic = xkcd.comic.get_current_comic()
    log.info(f"Current comic: {current_comic}")

    comic_serial = serialize_utils.serialize_dict(
        data=current_comic.model_dump(),
        output_dir=f"{SERIALIZE_DIR}/comic_responses",
        filename=f"{current_comic.comic_num}.msgpack",
    )

    update_comic_nums_file(comic_num=current_comic.comic_num)


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

    main()
