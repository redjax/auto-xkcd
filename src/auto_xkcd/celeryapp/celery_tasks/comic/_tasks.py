import typing as t
from pathlib import Path
import time

from core import request_client, database
from core.config import settings
from domain.xkcd import MultiComicRequestQueue, XKCDComic
from modules import xkcd_mod, celery_mod, requests_prefab
from packages import xkcd_comic

from loguru import logger as log
import httpx


@celery_mod.app.task(name="process_multiple_comic_requests")
def process_multi_comic_req_queue(
    request_queue: dict = None,
    loop_pause: int = 15,
    req_pause: int = 5,
):
    try:
        _convert_req_queue = MultiComicRequestQueue.model_validate(request_queue)
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
        log.debug(f"Partitions: {request_queue.queue_size}")
    else:
        log.debug(f"Requests in queue: {request_queue.queue_size}")

    if not request_queue.partitioned:
        log.info(f"Requesting [{request_queue.queue_size}] comic(s)")

        # comic_requests: list[httpx.Request] = []
        comic_objs: list[XKCDComic] = []

        for i in request_queue.queue:
            log.debug(f"Queue item: {i}")
            _comic: XKCDComic = xkcd_comic.comic.get_single_comic(comic_num=i)
            comic_objs.append(_comic)
            # req: httpx.Request = requests_prefab.comic_num_req(comic_num=i)
            # comic_requests.append(req)

        comic_return_dicts: list[dict] = []

        for _comic in comic_objs:
            comic_dict = _comic.model_dump()
            comic_return_dicts.append(comic_dict)

        return {"comics": comic_return_dicts}

    else:
        log.info(
            f"Request queue is partitoned. Processing [{len(request_queue.queue)}] queue(s), pausing {loop_pause} second(s) in between each loop."
        )

        current_partition: int = 1

        # request_batches: list[list[httpx.Request]] = []
        comic_requests: list[XKCDComic] = []
        batch_errored_urls: list[str] = []
        err_comic_ids: list[int] = []

        for partition in request_queue.queue:
            log.info(
                f"Processing partition [{current_partition}/{request_queue.queue_size}]"
            )
            log.debug(f"Partition size: {len(partition)}")

            partition_comic_responses: list[XKCDComic] = []

            for comic_num in partition:
                try:
                    _comic: XKCDComic = xkcd_comic.comic.get_single_comic(
                        comic_num=comic_num
                    )
                    partition_comic_responses.append(_comic)
                except Exception as exc:
                    msg = Exception(
                        f"Unhandled exception requesting comic #{comic_num}. Details: {exc}"
                    )
                    log.error(msg)
                    log.trace(exc)

                    err_comic_ids.append(comic_num)

                    continue

                log.info(f"Sleeping for {req_pause} second(s) between requests...")
                time.sleep(req_pause)

            comic_requests = comic_requests + partition_comic_responses
            log.info(
                f"Sleeping for {loop_pause} second(s) between partitioned requests..."
            )
            time.sleep(loop_pause)

        log.info(f"Requested [{len(comic_requests)}] comic(s)")

        comic_return_dicts: list[dict] = []

        for _comic in comic_requests:
            comic_dict = _comic.model_dump()
            comic_return_dicts.append(comic_dict)

        return {"comics": comic_return_dicts}
