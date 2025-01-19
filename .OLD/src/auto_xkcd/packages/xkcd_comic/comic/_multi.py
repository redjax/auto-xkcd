"""Handle multiple xkcd comic requests.

Idea:
A list of comic number becomes a request queue, and when a maximum queue size is breached, the queue is partitioned into smaller lists of integers.
These can be passed into "lanes," which will run Celery tasks.

A controller can limit the number of "lanes" available to avoid excessive requests to the XKCD comic API.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import time
import typing as t

from celery.result import AsyncResult
import celeryapp
from core.constants import IGNORE_COMIC_NUMS
from domain.xkcd import (
    MultiComicRequestQueue,
    XKCDComic,
    XKCDComicImage,
    XKCDComicImageModel,
    XKCDComicModel,
)
from loguru import logger as log
from modules import xkcd_mod
from packages import xkcd_comic
from red_utils.core.dataclass_utils import DictMixin
from utils.list_utils import prepare_list_shards

MAX_QUEUE_SIZE: int = 15


def get_multiple_comics(
    comic_nums_lst: list[int] = None, loop_pause: int = 15, req_pause: int = 5
) -> list[XKCDComic]:
    log.info(f"Requesting [{comic_nums_lst}] comic(s)")

    comic_objects: list[XKCDComic] = []
    err_comic_nums: list[int] = []

    for comic_num in comic_nums_lst:
        if comic_num in IGNORE_COMIC_NUMS:
            log.warning(f"Skipping ignored comic #{comic_num}")

            continue

        db_comic = None

        ## Load from database
        try:
            db_comic: XKCDComic | None = xkcd_mod.get_comic_from_db(comic_num=comic_num)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception getting XKCDComic from database. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

        _comic = db_comic
        if _comic:
            log.debug(f"Found comic #{comic_num} in database. Skipping request pause")
            comic_objects.append(_comic)

            continue

        log.debug(f"Did not find comic #{comic_num} in database.")
        log.debug(f"Searching for serialized comic #{comic_num}")
        try:
            _comic: XKCDComic = xkcd_mod.load_serialized_comic(comic_num=comic_num)

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception loading comic #{comic_num} from serialized Response file. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

        if _comic:
            log.debug(
                f"Found comic #{comic_num} in a serialized file. Skipping request pause"
            )
            comic_objects.append(_comic)

            continue

        ## Live HTTP request
        try:
            _comic: XKCDComic = xkcd_comic.comic.get_single_comic(comic_num=comic_num)
        except Exception as exc:
            msg = Exception(f"Unhandled exception requesting comic #{comic_num}")
            log.error(msg)
            log.trace(exc)

            err_comic_nums.append(comic_num)

        if _comic is None:
            log.warning(
                f"Could not load XKCD comic #{comic_num} from database, serialized file, or a live HTTP request. Does this comic exist? https://xkcd.com/{comic_num}"
            )
            continue

        comic_objects.append(_comic)

        log.info(f"Waiting for [{req_pause}] second(s) between requests...")
        time.sleep(req_pause)

    if err_comic_nums:
        log.warning(f"Errors: {err_comic_nums}")

    return comic_objects


def get_multiple_comics_task(
    comic_nums_lst: list[int] = None, loop_pause: int = 15, req_pause: int = 5
) -> AsyncResult | None:
    if len(comic_nums_lst) > MAX_QUEUE_SIZE:
        log.warning(
            f"Maximum comic request queue size limit exceeded [{len(comic_nums_lst)}/{MAX_QUEUE_SIZE}]. Queue will be partitioned"
        )

    comic_req_queue: MultiComicRequestQueue = MultiComicRequestQueue(
        queue=comic_nums_lst, max_queue_size=MAX_QUEUE_SIZE
    )
    log.debug(
        f"Comic queue size (partitioned: {comic_req_queue.partitioned}): [{comic_req_queue.queue_size}/{comic_req_queue.max_queue_size}]"
    )

    comic_req_queue.partition_queue()
    log.debug(
        f"Check 2: comic queue size (partitioned: {comic_req_queue.partitioned}): [part count: {comic_req_queue.queue_size}]"
    )

    if comic_req_queue.partitioned:
        log.info(
            f"Comic request queue is partitioned. Requesting [{len(comic_req_queue.queue)}] queue(s)"
        )
    else:
        log.info(
            f"Comic request queue is not partitioned. Requesting [{len(comic_req_queue.queue)}] comic(s)"
        )

    try:
        multi_comic_task = (
            celeryapp.celery_tasks.comic.task_process_multi_comic_req_queue.delay(
                comic_req_queue.model_dump(), loop_pause, req_pause
            )
        )

        return multi_comic_task

    except Exception as exc:

        msg = Exception(f"Unhandled exception getting multiple comics. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        return None
