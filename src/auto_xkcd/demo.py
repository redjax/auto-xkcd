from __future__ import annotations

from core.dependencies import settings
from core.paths import ENSURE_DIRS
from loguru import logger as log
from packages import demo
from red_utils.ext.loguru_utils import init_logger, sinks
from red_utils.std import path_utils

if __name__ == "__main__":
    init_logger(sinks=[sinks.LoguruSinkStdOut(level=settings.log_level).as_dict()])

    log.info(f"[DEMO] Start auto-xkcd")

    path_utils.ensure_dirs_exist(ensure_dirs=ENSURE_DIRS)

    log.info(">> Start demo")
    demo.demo_all(req_sleep=10)
    log.info("<< End demo")
