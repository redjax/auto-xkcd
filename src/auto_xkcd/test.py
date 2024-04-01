import typing as t
from pathlib import Path

from core.paths import ENSURE_DIRS
from core.dependencies import db_settings, get_db, settings
from modules import xkcd_mod
from packages import xkcd
from red_utils.ext.loguru_utils import init_logger, sinks
from red_utils.std import path_utils
from loguru import logger as log


if __name__ == "__main__":
    init_logger(sinks=[sinks.LoguruSinkStdOut(level=settings.log_level).as_dict()])

    log.info(f"Start auto-xkcd")

    path_utils.ensure_dirs_exist(ensure_dirs=ENSURE_DIRS)

    xkcd.helpers.update_comic_num_img_bool()
