import typing as t
from pathlib import Path

from core import request_client
from modules import xkcd_mod
from packages.xkcd.helpers import (
    ComicNumsController,
    url_hash,
    parse_comic_response,
    comic_num_hash,
    serialize_response,
)

from loguru import logger as log
import httpx


def get_comic(comic_num: t.Union[str, int] = None, save_serial: bool = True) -> dict:
    assert comic_num, ValueError("Missing a comic_num")
    assert isinstance(comic_num, str) or isinstance(comic_num, int), TypeError(
        f"comic_num must be of type str or dict. Got type: ({type(comic_num)})"
    )

    with ComicNumsController() as comic_nums_controller:
        comic_nums = comic_nums_controller.as_list()

    if comic_num in comic_nums:
        log.warning(f"Comic #{comic_num} has already been requested.")

    comic_req: httpx.Request = xkcd_mod.comic_num_req(comic_num=comic_num)

    with request_client.CACHE_TRANSPORT as transport:
        try:
            res: httpx.Response = request_client.simple_get(
                request=comic_req, transport=transport
            )
            log.info(
                f"Comic #{comic_num} response: [{res.status_code}: {res.reason_phrase}]"
            )
            _url_hash: str = url_hash(url=res.url)
            log.debug(f"URL hash: {_url_hash}")

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception requesting comic #{comic_num}. Details: {exc}"
            )
            log.error(msg)

            raise msg

    try:
        comic_dict: dict = parse_comic_response(res=res)
        comic_hash: str = comic_num_hash(comic_num=comic_dict["num"])
        log.debug(f"Comic num [{comic_dict['num']}] hash: {comic_hash}")

        ## Append hashes to response dict
        comic_dict["url_hash"] = url_hash

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception parsing current XKCD comic response. Details: {exc}"
        )
        log.error(msg)

        raise msg

    if save_serial:
        serial_filename: str = str(comic_dict["num"]) + ".msgpack"

        try:
            log.debug(f"Serialized filename: {serial_filename}")
            serialize_response(res=res, filename=serial_filename)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception serializing comic response. Details: {exc}"
            )
            log.error(msg)

    return comic_dict


def get_multiple_comics(
    comic_nums_list: list[t.Union[int, str]] = None, save_serial: bool = True
) -> list[dict]:
    assert comic_nums_list, ValueError("Missing list of comic_nums to request")
    assert isinstance(comic_nums_list, list), TypeError(
        f"comic_nums_list must be of type list. Got type: ({type(comic_nums_list)})"
    )

    comic_responses: list[httpx.Request] = []
    parsed_responses: list[dict] = []

    with ComicNumsController() as comic_nums_ctl:
        comic_nums: list[int] = comic_nums_ctl.as_list()

        for comic_num in comic_nums_list:
            assert comic_num, ValueError("Missing a comic_num")
            assert isinstance(comic_num, str) or isinstance(comic_num, int), TypeError(
                f"comic_num must be of type str or dict. Got type: ({type(comic_num)})"
            )

            if comic_num in comic_nums:
                log.warning(f"Comic #{comic_num} has already been requested")

            req: httpx.Request = xkcd_mod.comic_num_req(comic_num=comic_num)

            log.info(f"Requesting comic #{comic_num}")
            try:
                comic_res: httpx.Response = request_client.simple_get(request=req)

                log.info(
                    f"Comic #{comic_num} response: [{comic_res.status_code}: {comic_res.reason_phrase}]"
                )
                _url_hash: str = url_hash(url=comic_res.url)
                log.debug(f"URL hash: {_url_hash}")

                comic_responses.append(comic_res)

            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception requesting comic #{comic_num}. Details: {exc}"
                )
                log.error(msg)

                raise msg

        for r in comic_responses:
            try:
                comic_dict: dict = parse_comic_response(res=r)
                comic_hash: str = comic_num_hash(comic_num=comic_dict["num"])
                log.debug(f"Comic num [{comic_dict['num']}] hash: {comic_hash}")

                ## Append hashes to response dict
                comic_dict["url_hash"] = url_hash

                parsed_responses.append(comic_dict)

            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception parsing current XKCD comic response. Details: {exc}"
                )
                log.error(msg)

                raise msg

        if save_serial:
            for p in parsed_responses:
                serial_filename: str = str(p["num"]) + ".msgpack"

                try:
                    log.debug(f"Serialized filename: {serial_filename}")
                    serialize_response(res=r, filename=serial_filename)
                except Exception as exc:
                    msg = Exception(
                        f"Unhandled exception serializing comic response. Details: {exc}"
                    )
                    log.error(msg)

        return parsed_responses
