from __future__ import annotations

from core.dependencies import settings
from core.paths import ENSURE_DIRS
from loguru import logger as log
from packages import demo, xkcd
from red_utils.ext.loguru_utils import init_logger, sinks
from red_utils.std import path_utils

if __name__ == "__main__":
    init_logger(
        sinks=[
            sinks.LoguruSinkStdOut(level=settings.log_level).as_dict(),
            sinks.LoguruSinkAppFile(level=settings.log_level).as_dict(),
            sinks.LoguruSinkErrFile(level=settings.log_level).as_dict(),
        ]
    )

    log.info(f"[DEMO] Start auto-xkcd")

    path_utils.ensure_dirs_exist(ensure_dirs=ENSURE_DIRS)

    log.info("Updating img_saved bool column in CSV file.")
    _update_csv = xkcd.helpers.update_comic_num_img_bool()

    log.info(">> Start demo")
    demo.demo_all(req_sleep=10)
    log.info("<< End demo")

    log.info("Starting search for missing images")
    demo.demo_req_missing_imgs()
