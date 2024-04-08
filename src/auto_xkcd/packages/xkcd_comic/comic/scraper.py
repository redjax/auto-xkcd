import typing as t
from pathlib import Path

from core.paths import (
    COMIC_IMG_DIR,
    SERIALIZE_COMIC_OBJECTS_DIR,
    SERIALIZE_COMIC_RESPONSES_DIR,
)
from core import request_client
from domain.xkcd.comic.schemas import CurrentComicMeta, XKCDComic
from modules import xkcd_mod, requests_prefab
from helpers import data_ctl
from helpers.validators import (
    validate_comic_nums_lst,
    validate_hishel_cachetransport,
    validate_path,
)
from utils import list_utils
from .methods import get_multiple_comics, get_single_comic

from loguru import logger as log
import httpx
import hishel


def make_list_chunks(
    input_list: list[t.Any] = None, max_list_size: int = 50
) -> list[list[t.Any]] | list[t.Any]:
    """Break a list into smaller lists/"chunks" based on max_list_size.

    Params:
        input_list (list): The input list to be chunked.
        max_list_size (int): The maximum size of each chunk.

    Returns:
        list of lists: List of smaller lists or chunks.

    """
    assert input_list, ValueError("Missing input list to break into smaller chunks")
    assert isinstance(input_list, list), TypeError(
        f"input_list must be a list. Got type: ({type(input_list)})"
    )

    if max_list_size == 0 or max_list_size is None:
        log.warning(
            f"No limit set on list size. Returning full list embedded in another list"
        )

        return input_list

    chunked_list: list[list] = []
    ## Loop over objects in list, breaking into smaller list chunks each time
    #  the iterator reaches max_list_size
    for i in range(0, len(input_list), max_list_size):
        chunked_list.append(input_list[i : i + max_list_size])

    log.debug(
        f"Created [{len(chunked_list)}] list(s) of {max_list_size} or less items."
    )

    return chunked_list


def scrape_missing_comics(
    cache_transport: hishel.CacheTransport = None,
    request_sleep: int = 5,
    max_list_size: int = 50,
    loop_limit: int | None = None,
    overwrite_serialized_comic: bool = False,
) -> list[XKCDComic] | None:
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
        missing_nums_lists: list[list[int]] = make_list_chunks(
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

        try:
            missing_comics: list[XKCDComic] = get_multiple_comics(
                cache_transport=cache_transport, comic_nums=missing_comic_nums
            )

            return missing_comics

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception scraping missing comics. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            raise exc

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
