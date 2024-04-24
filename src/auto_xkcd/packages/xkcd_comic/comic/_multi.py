"""Handle multiple xkcd comic requests.

Idea:
A list of comic number becomes a request queue, and when a maximum queue size is breached, the queue is partitioned into smaller lists of integers.
These can be passed into "lanes," which will run Celery tasks.

A controller can limit the number of "lanes" available to avoid excessive requests to the XKCD comic API.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import typing as t

from domain.xkcd import (
    XKCDComic,
    XKCDComicImage,
    XKCDComicImageModel,
    XKCDComicModel,
    MultiComicRequestQueue,
)
from loguru import logger as log
from modules import xkcd_mod
from packages import xkcd_comic
import celeryapp
from red_utils.core.dataclass_utils import DictMixin
from utils.list_utils import prepare_list_shards

from celery.result import AsyncResult


MAX_QUEUE_SIZE: int = 15


def get_multiple_comics(
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

    if not comic_req_queue.partitioned:
        log.info(f"Requesting [{comic_req_queue.queue_size}] comic(s)")
    else:
        # loop_count: int = 1

        log.info(f"Looping over comic number queues")

        multi_comic_task = (
            celeryapp.celery_tasks.comic.process_multi_comic_req_queue.delay(
                comic_req_queue.model_dump(),
                loop_pause,
                req_pause,
            )
        )
        log.debug(
            f"Multi-comic request task ({type(multi_comic_task)}): {multi_comic_task}"
        )

        return multi_comic_task
