from __future__ import annotations
import time
from core import database
from core.dependencies import CACHE_TRANSPORT, db_settings, get_db, settings
from core.paths import DATA_DIR, ENSURE_DIRS, SERIALIZE_DIR
from core.request_client import HTTPXController, get_cache_transport
import hishel
import httpx
from loguru import logger as log
from modules import data_ctl, xkcd_mod
from modules.setup import _setup
import msgpack
from packages import xkcd
import pendulum
from pipelines import comic_pipelines
from red_utils.ext import time_utils
from red_utils.ext.loguru_utils import init_logger, sinks
from red_utils.std import path_utils
from utils import serialize_utils


def _run_current_comic_pipeline(
    cache_transport: hishel.CacheTransport = None, force_live_request: bool = False
) -> xkcd_mod.XKCDComic:
    log.info("Requesting current comic.")

    try:
        current_comic: xkcd_mod.XKCDComic = comic_pipelines.pipeline_get_current_comic(
            cache_transport=cache_transport, force_live_request=force_live_request
        )
    except Exception as exc:
        msg = Exception(f"Unhandled exception getting current comic. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc

    return current_comic


def main(
    cache_transport: hishel.CacheTransport = None,
    force_live_request: bool = False,
    max_loops: int | None = None,
    loop_pause: int | None = None,
) -> xkcd_mod.XKCDComic:
    loop_count: int = 1

    CONTINUE_LOOP: bool = True

    while CONTINUE_LOOP:
        if max_loops:
            if loop_count >= max_loops:
                log.warning(
                    f"Maximum loop count reached. Looped [{loop_count}/{max_loops}] times"
                )
                CONTINUE_LOOP = False
                continue

        log.info(f"[Loop count: {loop_count}] Requesting current comic")
        try:
            current_comic: xkcd_mod.XKCDComic = _run_current_comic_pipeline(
                cache_transport=cache_transport, force_live_request=force_live_request
            )
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception getting current comic. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            CONTINUE_LOOP = False
            continue

        log.info(f"Current comic: {current_comic}")

        loop_count += 1

        log.info(f"Sleeping for {loop_pause}s ...")
        time.sleep(loop_pause)

    log.info(
        f"Finished requesting current comic on a loop. Looped [{loop_count}] time(s)"
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

    cache_transport: hishel.CacheTransport = get_cache_transport(retries=3)

    ## 1 hour
    loop_pause = 3600

    main(
        cache_transport=cache_transport,
        force_live_request=False,
        max_loops=None,
        loop_pause=loop_pause,
    )
