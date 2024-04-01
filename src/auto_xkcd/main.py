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
    pipeline_update_img_saved_vals()


if __name__ == "__main__":
    init_logger(sinks=[sinks.LoguruSinkStdOut(level=settings.log_level).as_dict()])

    log.info(f"Start auto-xkcd")

    _setup()

    main()
