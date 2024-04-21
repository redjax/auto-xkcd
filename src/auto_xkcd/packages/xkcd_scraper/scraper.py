"""Handle scraping the XKCD API for missing comics."""

from __future__ import annotations

from pathlib import Path
import typing as t

from core import request_client
from core.paths import (
    COMIC_IMG_DIR,
    SERIALIZE_COMIC_OBJECTS_DIR,
    SERIALIZE_COMIC_RESPONSES_DIR,
)
from domain.xkcd.comic.schemas import CurrentComicMeta, XKCDComic
from helpers import data_ctl
from helpers.validators import (
    validate_comic_nums_lst,
    validate_hishel_cachetransport,
    validate_path,
)
import hishel
import httpx
from loguru import logger as log
from modules import requests_prefab, xkcd_mod
from utils import list_utils

def scrape_missing_comics(
    cache_transport: hishel.CacheTransport = None,
    request_sleep: int = 5,
    max_list_size: int = 50,
    loop_limit: int | None = None,
    overwrite_serialized_comic: bool = False,
) -> list[XKCDComic] | None:
    """Compile a list of missing comic numbers from saved comic images, then request those missing comics.

    Params:
        cache_transport (hishel.CacheTransport): A cache transport for the request client.
        request_sleep (int): [Default: 5] Number of seconds to sleep between requests.
        max_list_size (int): [Default: 50] If list size exceeds `max_list_size`, break list into smaller "chunks,"
            then return a "list of lists", where each inner list is a "chunk" of 50 comic images.
        loop_limit (int|None): [Default: None] Maximum number of times to loop, regardless of total number of missing comics.
        overwrite_serialized_comic (bool): If `True`, overwrite existing serialized file with data from request.

    Returns:
        (list[XKCDComic]): A list of scraped XKCDComic objects.

    """
    cache_transport = validate_hishel_cachetransport(cache_transport=cache_transport)

    ## Flip to True is list becomes chunked
    LIST_CHUNKED: bool = False

    log.info(f"Finding missing comic numbers")
    missing_comic_nums: list[int] = xkcd_mod.list_missing_nums()

    if not missing_comic_nums:
        log.warning(f"No missing comics found.")

        return

    if len(missing_comic_nums) > max_list_size:
        log.warning(
            f"Number of missing comics ({len(missing_comic_nums)}) is greater than the configured max_list_size ({max_list_size}). Breaking into smaller chunks"
        )
        missing_nums_lists: list[list[int]] = list_utils.make_list_chunks(
            input_list=missing_comic_nums, max_list_size=max_list_size
        )

        LIST_CHUNKED = True

    else:
        log.debug(
            f"Number of missing comics [{len(missing_comic_nums)}] is below configured max_list_size ({max_list_size}). Continuing without breaking list into smaller chunks"
        )

    log.debug(f"List broken into smaller chunks: {LIST_CHUNKED}")

    if not LIST_CHUNKED:
        ## List count is below max_list_size.

        raise NotImplementedError(f"Requesting multiple comics is not yet implemented")

        # try:
        #     missing_comics: list[XKCDComic] = get_multiple_comics(
        #         cache_transport=cache_transport, comic_nums=missing_comic_nums
        #     )

        #     return missing_comics

        # except Exception as exc:
        #     msg = Exception(
        #         f"Unhandled exception scraping missing comics. Details: {exc}"
        #     )
        #     log.error(msg)
        #     log.trace(exc)

        #     raise exc

    else:
        ## List size is greater than max_list_size. Break into smaller chunks & loop

        LIST_LOOP_COUNTER: int = 1
        MAX_LOOPS: int = len(missing_nums_lists)
        CONTINUE_LOOP: bool = True

        COMIC_OBJ_LISTS: list[list[XKCDComic]] = []

        log.info(f"Looping over [{MAX_LOOPS}] list(s) of missing comics.")

        while CONTINUE_LOOP:

            if LIST_LOOP_COUNTER >= MAX_LOOPS:
                log.debug(
                    f"Looped [{LIST_LOOP_COUNTER}/{MAX_LOOPS}] times. Exiting loop"
                )
                CONTINUE_LOOP = False
                break

            for lst in missing_nums_lists:
                log.debug(f"Loop [{LIST_LOOP_COUNTER}/{MAX_LOOPS}]")
                log.debug(f"List item(s): {len(lst)}")

                raise NotImplementedError(
                    f"Requesting multiple comics is not yet implemented"
                )

                _comics: list[XKCDComic] = get_multiple_comics(
                    cache_transport=cache_transport,
                    comic_nums=lst,
                    overwrite_serialized_comic=overwrite_serialized_comic,
                    request_sleep=request_sleep,
                )
                COMIC_OBJ_LISTS.append(_comics)

                LIST_LOOP_COUNTER += 1

        log.debug(
            f"Joining [{len(COMIC_OBJ_LISTS)}] lists of XKCDComic objects into single list"
        )
        try:
            joined_list: list[XKCDComic] = list_utils.join_list_of_lists(
                COMIC_OBJ_LISTS
            )

            return joined_list

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception joining chunked lists of XKCDComic objects into single list. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            raise exc
