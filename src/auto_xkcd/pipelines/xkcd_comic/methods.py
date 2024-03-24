import typing as t

from packages import xkcd
from modules import xkcd_mod
from core import request_client

import httpx
import hishel
from loguru import logger as log
from red_utils.std import hash_utils


def pipeline_current_comic(
    transport: hishel.CacheTransport = request_client.CACHE_TRANSPORT,
    save_serial: bool = True,
    save_to_db: bool = False,
) -> xkcd_mod.XKCDComic:
    if not transport:
        transport: hishel.CacheTransport = request_client.CACHE_TRANSPORT
    try:
        current_comic_res: httpx.Response = xkcd.request_current_comic()
        url_hash: str = xkcd.helpers.url_hash(url=current_comic_res.url)
        log.debug(f"URL hash: {url_hash}")

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting current XKCD comic. Details: {exc}"
        )

        raise msg

    log.info(">> Start current comic pipeline")

    try:
        current_comic_dict: dict = xkcd.helpers.parse_comic_response(
            res=current_comic_res
        )
        comic_hash: str = xkcd.helpers.comic_num_hash(
            comic_num=current_comic_dict["num"]
        )
        log.debug(f"Comic num [{current_comic_dict['num']}] hash: {comic_hash}")

        ## Append hashes to response dict
        current_comic_dict["url_hash"] = url_hash

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception parsing current XKCD comic response. Details: {exc}"
        )
        log.error(msg)

        raise msg

    current_comic: xkcd_mod.XKCDComic = xkcd_mod.XKCDComic().model_validate(
        current_comic_dict
    )
    # log.info(f"Current comic: {current_comic}")

    if save_serial:
        serial_filename: str = str(current_comic_dict["num"]) + ".msgpack"

        try:
            log.debug(f"Serialized filename: {serial_filename}")
            xkcd.helpers.serialize_response(
                res=current_comic_res, filename=serial_filename
            )
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception serializing comic response. Details: {exc}"
            )
            log.error(msg)

    if save_to_db:
        log.warning(
            f"save_to_db=True, but method is not yet implemented. Skipping save to database."
        )
        pass

    with xkcd.helpers.ComicNumsController() as comic_nums:
        data = xkcd_mod.ComicNumCSVData(
            comic_num=current_comic.comic_num, img_saved=False
        )

        comic_nums.add_comic_num_data(data.model_dump())

    log.info("<< End current comic pipeline")

    return current_comic


def pipeline_random_comic(
    save_serial: bool = True,
    save_to_db: bool = False,
    transport: hishel.CacheTransport = request_client.CACHE_TRANSPORT,
) -> xkcd_mod.XKCDComic:
    if not transport:
        transport: hishel.CacheTransport = request_client.CACHE_TRANSPORT

    random_comic_res: httpx.Response = xkcd.get_random_comic(transport=transport)
    # log.debug(f"Random comic response: {random_comic_res}")

    random_comic_dict = xkcd.helpers.parse_comic_response(res=random_comic_res)

    log.info(">> Start random comic pipeline")

    try:
        comic_hash: str = xkcd.helpers.comic_num_hash(
            comic_num=random_comic_dict["num"]
        )
        log.debug(f"Comic num [{random_comic_dict['num']}] hash: {comic_hash}")

        ## Append hashes to response dict
        random_comic_dict["url_hash"] = xkcd.helpers.url_hash(url=random_comic_res.url)

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception parsing current XKCD comic response. Details: {exc}"
        )
        log.error(msg)

        raise msg

    random_comic: xkcd_mod.XKCDComic = xkcd_mod.XKCDComic().model_validate(
        random_comic_dict
    )
    # log.debug(f"Random comic: {random_comic}")

    with xkcd.helpers.ComicNumsController() as comic_nums:
        random_comic_data = xkcd_mod.ComicNumCSVData(
            comic_num=random_comic.comic_num, img_saved=False
        )
        comic_nums.add_comic_num_data(random_comic_data.model_dump())

    if save_serial:
        serial_filename: str = str(random_comic_dict["num"]) + ".msgpack"

        try:
            log.debug(f"Serialized filename: {serial_filename}")
            xkcd.helpers.serialize_response(
                res=random_comic_res, filename=serial_filename
            )
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception serializing comic response. Details: {exc}"
            )
            log.error(msg)

    if save_to_db:
        log.warning(
            f"save_to_db=True, but method is not yet implemented. Skipping save to database."
        )
        pass

    with xkcd.helpers.ComicNumsController() as comic_nums:
        data = xkcd_mod.ComicNumCSVData(
            comic_num=random_comic.comic_num, img_saved=False
        )

        comic_nums.add_comic_num_data(data.model_dump())

    log.info("<< End random comic pipeline")

    return random_comic


def pipeline_specific_comic(
    comic_num: t.Union[str, int] = None,
    transport: hishel.CacheTransport = request_client.CACHE_TRANSPORT,
    save_serial: bool = True,
    save_to_db: bool = False,
) -> xkcd_mod.XKCDComic:
    assert comic_num, ValueError("Missing comic number for pipeline")
    assert isinstance(comic_num, str) or isinstance(comic_num, int), TypeError(
        f"comic_num should be a string or integer. Got type: ({type(comic_num)})"
    )

    if not transport:
        transport: hishel.CacheTransport = request_client.CACHE_TRANSPORT

    log.info(">> Start specific comic pipeline")

    try:
        comic_res: httpx.Response = xkcd.get_comic(
            comic_num=comic_num, transport=transport
        )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception requesting comic #{comic_num}. Details: {exc}"
        )
        log.error(msg)

        raise msg

    try:
        comic_dict: dict = xkcd.helpers.parse_comic_response(res=comic_res)
        comic_num_hash: str = xkcd.helpers.comic_num_hash(comic_num=comic_dict["num"])
        log.debug(f"Comic num [{comic_dict['num']}] hash: {comic_num_hash}")

        ## Append hashes to response dict
        comic_dict["url_hash"] = hash_utils.get_hash_from_str(input_str=comic_res.url)
        log.debug(f"URL hash: {comic_dict['url_hash']}")

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception parsing current XKCD comic response. Details: {exc}"
        )
        log.error(msg)

        raise msg

    comic: xkcd_mod.XKCDComic = xkcd_mod.XKCDComic.model_validate(comic_dict)

    if save_serial:
        serial_filename: str = str(comic_dict["num"]) + ".msgpack"

        try:
            log.debug(f"Serialized filename: {serial_filename}")
            xkcd.helpers.serialize_response(res=comic_res, filename=serial_filename)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception serializing comic response. Details: {exc}"
            )
            log.error(msg)

    if save_to_db:
        log.warning(
            f"save_to_db=True, but method is not yet implemented. Skipping save to database."
        )
        pass

    with xkcd.helpers.ComicNumsController() as comic_nums:
        data = xkcd_mod.ComicNumCSVData(comic_num=comic.comic_num, img_saved=False)

        comic_nums.add_comic_num_data(data.model_dump())

    log.info("<< End specific comic pipeline")

    return comic


def pipeline_multiple_comics(
    comic_nums_list: list[int] = None,
    transport: hishel.CacheTransport = request_client.CACHE_TRANSPORT,
    save_serial: bool = True,
    save_to_db: bool = False,
) -> list[xkcd_mod.XKCDComic]:
    assert comic_nums_list, ValueError("Missing list of comic_nums to request")
    assert isinstance(comic_nums_list, list), TypeError(
        f"comic_nums_list must be a list of ints. Got type: ({type(comic_nums_list)})"
    )
    for i in comic_nums_list:
        assert isinstance(i, str) or isinstance(i, int), TypeError(
            f"Each value in comic_nums_list must be an integer or string. Got type: ({type(i)}) for value '{i}'."
        )

    log.info(">> Start multi-comic pipeline")

    multiple_comics_res: list[httpx.Response] = xkcd.get_multiple_comics(
        comic_nums_list=comic_nums_list
    )

    multiple_comic_dicts: list[dict] = []
    multiple_comics: list[xkcd_mod.XKCDComic] = []

    for r in multiple_comics_res:
        p: dict = xkcd.helpers.parse_comic_response(res=r)
        multiple_comic_dicts.append(p)

        c: xkcd_mod.XKCDComic = xkcd_mod.XKCDComic.model_validate(p)
        multiple_comics.append(c)

    if save_serial:
        for c in multiple_comics:
            serial_filename: str = str(c.comic_num) + ".msgpack"

            try:
                log.debug(f"Serialized filename: {serial_filename}")
                xkcd.helpers.serialize_response(res=r, filename=serial_filename)
            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception serializing comic response. Details: {exc}"
                )
                log.error(msg)

    if save_to_db:
        log.warning(
            f"save_to_db=True, but method is not yet implemented. Skipping save to database."
        )
        pass

    with xkcd.helpers.ComicNumsController() as comic_nums:
        for c in multiple_comics:

            comic_data: xkcd_mod.ComicNumCSVData = xkcd_mod.ComicNumCSVData(
                comic_num=c.comic_num, img_saved=False
            )
            comic_nums.add_comic_num_data(comic_data.model_dump())

    log.info("<< End multi-comic pipeline")

    return multiple_comics
