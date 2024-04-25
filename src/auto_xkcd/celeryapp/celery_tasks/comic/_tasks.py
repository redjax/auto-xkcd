from __future__ import annotations

from pathlib import Path
import time
import typing as t

from celery.result import AsyncResult
from core import database, request_client
from core.constants import IGNORE_COMIC_NUMS
from core.config import settings
from domain.xkcd import MultiComicRequestQueue, XKCDComic
import httpx
from loguru import logger as log
from modules import celery_mod, requests_prefab, xkcd_mod
from packages import xkcd_comic


@celery_mod.app.task(name="process_multiple_comic_requests")
def process_multi_comic_req_queue(
    request_queue: dict = None,
    loop_pause: int = 10,
    req_pause: int = 5,
) -> dict[str, t.Any] | None:
    try:
        _convert_req_queue: MultiComicRequestQueue = (
            MultiComicRequestQueue.model_validate(request_queue)
        )
        request_queue: MultiComicRequestQueue = _convert_req_queue
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception converting incoming dict to MultiComicRequestQueue object. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        return None

    log.info(f"Incoming multi-comic request queue")
    log.debug(f"Request queue partitioned: {request_queue.partitioned}")

    if request_queue.partitioned:
        ## Partitioned queue
        log.debug(f"Partitions: {request_queue.queue_size}")

        partition_count: int = 1

        comic_objects: list[XKCDComic] = []
        comic_dicts: list[dict] = []
        err_comic_nums: list[int] = []

        for partition in request_queue.queue:
            log.info(
                f"Processing comic request queue partition [{partition_count}/{len(request_queue.queue)}]"
            )

            try:
                partition_results: list[XKCDComic] = (
                    xkcd_comic.comic.get_multiple_comics(
                        comic_nums_lst=partition,
                        loop_pause=loop_pause,
                        req_pause=req_pause,
                    )
                )
            except Exception as exc:
                msg = Exception(f"Unhandled exception getting comics. Details: {exc}")
                log.error(msg)
                log.trace(exc)

                continue

            comic_objects = comic_objects + partition_results

        for comic_obj in comic_objects:
            comic_dict: dict = comic_obj.model_dump()
            comic_dicts.append(comic_dict)

        return_obj = {"comics": comic_dicts, "errors": err_comic_nums}

        return return_obj

    else:
        ## Non-partitioned queue

        log.info(f"Requesting [{request_queue.queue_size}] comic(s)")

        # comic_objects: list[XKCDComic] = []
        comic_dicts: list[dict] = []
        err_comic_nums: list[int] = []

        try:
            comic_objects: list[XKCDComic] = xkcd_comic.comic.get_multiple_comics(
                comic_nums_lst=request_queue.queue,
                loop_pause=loop_pause,
                req_pause=req_pause,
            )
        except Exception as exc:
            msg = Exception(f"Unhandled exception getting comics. Details: {exc}")
            log.error(msg)
            log.trace(exc)

        for comic_obj in comic_objects:
            comic_dict: dict = comic_obj.model_dump()
            comic_dicts.append(comic_dict)

        return_obj = {"comics": comic_dicts, "errors": err_comic_nums}

        return return_obj
