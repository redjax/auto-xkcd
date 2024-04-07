import typing as t
import time
from pathlib import Path

from core.paths import SERIALIZE_DIR, COMIC_IMG_DIR
from core.request_client import HTTPXController, save_bytes
from modules import xkcd_mod, data_ctl
from utils import serialize_utils

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


def get_specific_comic(
    cache_transport: hishel.CacheTransport = None, comic_num: int = None
) -> xkcd_mod.XKCDComic:
    comic_url: str = f"{xkcd_mod.XKCD_URL_BASE}/{comic_num}/{xkcd_mod.XKCD_URL_POSTFIX}"
    comic_res: httpx.Response = request_comic(
        url=comic_url, cache_transport=cache_transport
    )
    log.debug(
        f"Comic #{comic_num} response: [{comic_res.status_code}: {comic_res.reason_phrase}]"
    )
    comic_dict: dict = convert_response_to_dict(res=comic_res)
    log.debug(f"Comic #{comic_num} res dict: {comic_dict}")
    comic: xkcd_mod.XKCDComic = convert_dict_to_xkcdcomic(_dict=comic_dict)
    log.debug(f"Comic #{comic_num}: {comic_num}")

    return comic


def get_multiple_comics(
    comic_nums: list[int] = None,
    cache_transport: hishel.CacheTransport = None,
    request_sleep: int = 5,
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

        try:
            ## Serialize comic to msgpack file
            serialize_utils.serialize_dict(
                data=comic.model_dump(),
                output_dir=f"{SERIALIZE_DIR}/comic_responses",
                filename=f"{comic.num}.msgpack",
            )
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception serializing comic #{comic.num} response. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

        try:
            comic_saved: bool = save_img(
                comic=comic, output_filename=f"{comic.num}.png"
            )
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception saving comic #{comic.num} image. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

        log.info(f"Sleeping for {request_sleep}s between requests...")
        time.sleep(request_sleep)

    return comics


def save_img(
    comic: t.Union[httpx.Response, xkcd_mod.XKCDComic, dict],
    output_dir: t.Union[str, Path] = COMIC_IMG_DIR,
    output_filename: str = None,
    cache_transport: hishel.CacheTransport = None,
):
    assert comic, ValueError("Missing a comic object")
    assert isinstance(comic, httpx.Response) or isinstance(
        comic, xkcd_mod.XKCDComic
    ), TypeError(
        f"comic must be of type httpx.Response or xkcd_mod.XKCDComic. Got type: ({type(comic)})"
    )
    if isinstance(comic, httpx.Response):
        log.warning(
            f"Input comic is an httpx Response. Converting to XKCDComic instance."
        )
        with HTTPXController() as httpx_ctl:
            comic_dict: dict = httpx_ctl.decode_res_content(res=comic)
            _comic: xkcd_mod.XKCDComic = xkcd_mod.XKCDComic.model_validate(comic_dict)

        comic: xkcd_mod.XKCDComic = _comic

    if isinstance(comic, dict):
        log.warning(f"Input comic is a dict. Converting to XKCDComic instance.")
        _comic: xkcd_mod.XKCDComic = xkcd_mod.XKCDComic.model_validate(comic)
        comic: xkcd_mod.XKCDComic = _comic
        log.debug(f"Converted comic dict to XKCDComic ({type(comic)}): {comic}")

    assert output_dir, ValueError("Missing output directory path")
    assert isinstance(output_dir, str) or isinstance(output_dir, Path), TypeError(
        f"output_dir must be a str or Path. Got type: ({type(output_dir)})"
    )
    if isinstance(output_dir, Path):
        if "~" in f"{output_dir}":
            _dir: Path = output_dir.expanduser()
            output_dir = _dir
    elif isinstance(output_dir, str):
        if "~" in output_dir:
            output_dir: Path = Path(output_dir).expanduser()
        else:
            output_dir: Path = Path(output_dir)

    assert output_filename, ValueError("Missing output filename")
    assert isinstance(output_filename, str), TypeError(
        f"output_filename must be a string. Got type: ({type(output_filename)})"
    )

    try:
        saved_imgs: list[int] = data_ctl.get_saved_imgs()
        if saved_imgs is None:
            log.warning(f"Did not find any saved images in path '{output_dir}'.")

            return False

        if isinstance(saved_imgs, list):
            log.debug(
                f"Found [{len(saved_imgs)}] saved image(s) in path '{output_dir}'."
            )
        else:
            log.error(
                f"saved_imgs should be a list of integers. Got type: ({type(saved_imgs)})"
            )

            return False

    except Exception as exc:
        msg = Exception(f"Could not load saved comic image numbers. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc

    if comic.num in saved_imgs:
        log.warning(f"Comic #{comic.num} image has already been saved. Skipping.")

        return True

    if comic.img_url is None:
        log.debug(f"⚠️  Detected empty comic.img_url: {comic}")
        log.warning(
            f"Image URL for comic #{comic.num}' is None. Requesting comic #{comic.num} to get image URL"
        )

        ## Re-request comic response
        try:
            _comic_new: xkcd_mod.XKCDComic = get_specific_comic(
                cache_transport=cache_transport, comic_num=comic.num
            )
            comic: xkcd_mod.XKCDComic = _comic_new
            log.debug(f"Updated comic #{comic.num}: {comic}")

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception refreshing img_url for comic #{comic.num}. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            raise exc

        ## Serialize response
        try:
            serialize_utils.serialize_dict(
                data=comic.model_dump(),
                output_dir=f"{SERIALIZE_DIR}/comic_responses",
                filename=f"{comic.num}.msgpack",
                overwrite=True,
            )
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception serializing comic #{comic.num} response. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            raise exc

        ## Get img bytes
        try:
            with HTTPXController(transport=cache_transport) as httpx_ctl:
                req: httpx.Request = httpx_ctl.new_request(url=comic.img_url)
                res: httpx.Response = httpx_ctl.client.send(request=req)

            img_bytes: bytes = res.content

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception requesting comic #{comic.num} image bytes. Details: {exc}"
            )
            log.error(msg)
            log.trace(msg)

            raise exc

    else:
        ## Found comic.img_url, request img bytes
        try:
            with HTTPXController(transport=cache_transport) as httpx_ctl:
                req: httpx.Request = httpx_ctl.new_request(url=comic.img_url)
                res: httpx.Response = httpx_ctl.client.send(request=req)

            img_bytes: bytes = res.content

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception requesting comic #{comic.num} image bytes. Details: {exc}"
            )
            log.error(msg)
            log.trace(msg)

            raise exc

    _saved: bool = save_bytes(
        img_bytes=img_bytes, output_dir=output_dir, output_filename=output_filename
    )
    if not _saved:
        log.warning(f"Could not save image for comic #{comic.num}")
        return False

    return True
