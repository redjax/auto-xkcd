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

from domain.xkcd import XKCDComic, XKCDComicImage, XKCDComicImageModel, XKCDComicModel
from loguru import logger as log
from modules import xkcd_mod
from packages import xkcd_comic
from red_utils.core.dataclass_utils import DictMixin

@dataclass
class MultiComicRequestQueue(DictMixin):
    queue: list[int] | list[list] = field(default=None)
    partitioned: bool = field(default=False)
    max_queue_size: int = field(default=15)

    @property
    def queue_size(self) -> int:
        if self.queue is None:
            return 0
        elif isinstance(self.queue[0], int):
            return len(self.queue)
        elif isinstance(self.queue[0], list):
            queue_count = 0

            for q in self.queue:
                queue_count += 1

            return queue_count

    def partition_queue(self) -> list[int] | list[list[int]]:
        _partitioned: list[list[int]] = prepare_list_shards(original_list=self.queue)

        if isinstance(_partitioned[0], list):
            self.queue = _partitioned
            self.partitioned = True

        return _partitioned


def prepare_list_shards(
    original_list: list = [], shards: int = 1, shard_size_limit: int = 15
) -> list[list[t.Any]]:
    """Accept an input list. If size of list > set shard_size_limit, break into list of smaller lists.

    Params:
        original_list (list): A list with a lot of objects.
        shards (int) | default=1: The number of shards to create. This value is dynamic; as the function loops, more
            shards will be added as needed.
        shard_size_limit (int) | default=2000: The size limit for individual list shards as the original_list is broken into smaller lists.

    Returns:
        (list[list[Any]]): A list of smaller lists.

    """

    def create_list_shards(
        in_list=original_list, shards=shards, shard_size_limit=shard_size_limit
    ) -> list[t.Any] | list[list[t.Any]]:
        """Sub function that loops until all shards are individually smaller than shard_size_limit."""
        ## Number of items in original list
        list_len: int = len(in_list)
        ## Divide by number of shards to get individual shard size
        shard_size: int = int(list_len / shards)

        if shard_size > shard_size_limit:
            ## Individual shards still too large
            exceeds_by: int = shard_size - shard_size_limit
            print(
                f"Individual shard size [{shard_size}] exceed shard size limit of [{shard_size_limit}] by [{exceeds_by}]. Creating additional shard."
            )

            ## Add another shard, then loop
            shards += 1
            sharded_list: list = create_list_shards(
                in_list=in_list, shards=shards, shard_size_limit=shard_size_limit
            )
        else:
            ## Shard size limit satisfied, build new list of sub-lists (shards) & return
            sharded_list: list = [
                in_list[i : i + shard_size] for i in range(0, len(in_list), shard_size)
            ]

            print(
                f"Created [{len(sharded_list)}] shards. Individual shard size: [{len(sharded_list[0])}]"
            )

        return sharded_list

    if len(original_list) <= shard_size_limit:
        log.debug(
            f"List does not need paritioning. Size: [{len(original_list)}/{shard_size_limit}]"
        )

        return original_list

    list_of_shards: list[t.Any] | list[list[t.Any]] = create_list_shards()

    return list_of_shards


MAX_QUEUE_SIZE: int = 15


def get_multiple_comics(comic_nums_lst: list[int] = None):
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
        loop_count: int = 1

        log.info(f"Looping over comic number queues")

        for queue_part in comic_req_queue.queue:
            log.info(
                f"Queue [{loop_count}/{comic_req_queue.queue_size}] size: {len(queue_part)}"
            )

            loop_count += 1
