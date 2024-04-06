import typing as t
from core.request_client import HTTPXController
from modules import xkcd_mod

from loguru import logger as log

import hishel
import httpx


def request_comic(
    url: str = None, cache_transport: hishel.CacheTransport = None
) -> None | httpx.Response:
    assert url, ValueError("Missing a URL")
    assert isinstance(url, str), TypeError(f"url must be a string")

    with HTTPXController(transport=cache_transport) as httpx_ctl:

        req: httpx.Request = httpx_ctl.new_request(url=url)

        try:
            comic_res: httpx.Response = httpx_ctl.send_request(request=req)

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception getting current XKCD comic. Details: {exc}"
            )
            log.error(msg)

            raise exc

        if not comic_res.status_code == 200:
            log.warning(
                f"Non-200 response: [{comic_res.status_code}: {comic_res.reason_phrase}]: {comic_res.text}"
            )
            return

        return comic_res


def convert_response_to_dict(res: httpx.Response = None) -> dict:
    assert res, ValueError("Missing an httpx.Response object.")
    assert isinstance(res, httpx.Response), TypeError(
        f"res must be an httpx.Response object. Got type: ({type(res)})"
    )

    with HTTPXController() as httpx_ctl:
        try:
            comic_dict: dict = httpx_ctl.decode_res_content(res=res)

            return comic_dict
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception decoding comic response bytes. Details: {exc}"
            )
            log.error(msg)

            raise exc


def convert_dict_to_xkcdcomic(_dict: dict = None) -> xkcd_mod.XKCDComic:
    assert _dict, ValueError("Missing a dict input")
    assert isinstance(_dict, dict), TypeError(
        f"_dict input must be a dict object. Got type: ({type(_dict)})"
    )

    try:
        comic: xkcd_mod.XKCDComic = xkcd_mod.XKCDComic.model_validate(_dict)

        return comic
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception converting current comic dict to XKCDComic object. Details: {exc}"
        )
        log.error(msg)

        raise exc


def get_current_comic(
    cache_transport: hishel.CacheTransport = None,
) -> None | xkcd_mod.XKCDComic:
    _comic: None | httpx.Response = request_comic(
        url=xkcd_mod.CURRENT_XKCD_URL, cache_transport=cache_transport
    )
    # log.debug(f"Current comic response ({type(_comic)}): {_comic}")

    comic_dict: dict = convert_response_to_dict(res=_comic)
    # log.debug(f"Current comic response dict ({type(comic_dict)}): {comic_dict}")
    comic: xkcd_mod.XKCDComic = convert_dict_to_xkcdcomic(_dict=comic_dict)
    # log.debug(f"Current XKCD Comic ({type(comic)}): {comic}")
    comic.link = f"{xkcd_mod.XKCD_URL_BASE}/{comic.num}"

    return comic


def get_multiple_comics(
    comic_nums: list[int] = None, cache_transport: hishel.CacheTransport = None
) -> list[xkcd_mod.XKCDComic]:
    assert comic_nums, ValueError("Missing comic_nums list")
    assert isinstance(comic_nums, list), TypeError(
        f"comic_nums must be a list of integers. Got type: ({type(comic_nums)})"
    )

    log.info(f"Requesting [{len(comic_nums)}] comic(s)")

    comic_responses: list[httpx.Response] = []
    comic_dicts: list[dict] = []
    comics: list[xkcd_mod.XKCDComic] = []

    for c in comic_nums:
        if not isinstance(c, int):
            log.error(
                TypeError(
                    f"Comic numbers in comic_nums list must be integers. Got type: ({type(c)})"
                )
            )
            continue

        c_url: str = f"{xkcd_mod.XKCD_URL_BASE}/{c}/{xkcd_mod.XKCD_URL_POSTFIX}"
        # log.debug(f"Requesting comic URL: {c_url}")

        comic_res: httpx.Response = request_comic(
            url=c_url, cache_transport=cache_transport
        )
        if not comic_res:
            log.warning(f"Unable to request comic #{c}.")
            continue
        comic_responses.append(comic_res)

        comic_dict: dict = convert_response_to_dict(res=comic_res)
        if not comic_dict:
            log.warning(f"Unable to convert comic #{c} Response to dict.")
            continue
        comic_dicts.append(comic_dict)

        comic: xkcd_mod.XKCDComic = convert_dict_to_xkcdcomic(_dict=comic_dict)
        if not comic:
            log.warning(f"Unable to convert comic #{c} dict to XKCDComic.")
            continue
        comics.append(comic)

    return comics
