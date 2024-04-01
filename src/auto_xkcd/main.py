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


def main():
    raise NotImplementedError(
        "This app does not have a main.py entrypoint yet. Try running demo.py instead."
    )


if __name__ == "__main__":
    init_logger(sinks=[sinks.LoguruSinkStdOut(level=settings.log_level).as_dict()])

    log.info(f"Start auto-xkcd")

    path_utils.ensure_dirs_exist(ensure_dirs=ENSURE_DIRS)

    main()
