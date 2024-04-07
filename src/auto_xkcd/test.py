import typing as t
from pathlib import Path

from core.dependencies import settings
from core import (
    request_client,
    XKCD_URL_POSTFIX,
    XKCD_URL_BASE,
    CURRENT_XKCD_URL,
    SERIALIZE_COMIC_RESPONSES_DIR,
    SERIALIZE_COMIC_OBJECTS_DIR,
    COMIC_IMG_DIR,
)
from domain.xkcd.comic import XKCDComic
from _setup import base_app_setup
from modules import requests_prefab
from modules import xkcd_mod
from utils import serialize_utils

from loguru import logger as log

import httpx
import hishel


def _get_current_comic_res(
    cache_transport: hishel.CacheTransport = None,
) -> httpx.Response:
    try:
        current_comic_req: httpx.Request = requests_prefab.current_comic_req()

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting current comic request prefab. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    try:
        with request_client.HTTPXController(transport=cache_transport) as httpx_ctl:
            res: httpx.Response = httpx_ctl.send_request(request=current_comic_req)
            log.debug(
                f"Current comic response: [{res.status_code}: {res.reason_phrase}]"
            )

            if not res.status_code == 200:
                log.warning(
                    f"Non-200 status code: [{res.status_code}: {res.reason_phrase}]: {res.text}"
                )

                raise NotImplementedError(
                    f"Error handling for non-200 status codes not yet implemented."
                )

        log.success(f"Current XKCD comic requested")

    except Exception as exc:
        msg = Exception(f"Unhandled exception requesting current comic. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc

    return res


def _get_current_comic_dict_from_res(res: httpx.Response = None) -> dict:
    try:
        res_dict = xkcd_mod.response_handler.convert_response_to_dict(res=res)
        log.success(f"Converted Response to dict")

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception converting httpx.Response object to dict. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    return res_dict


def _serialize_current_comic_dict(res_dict: dict = None):
    try:
        serialize_utils.serialize_dict(
            data=res_dict,
            output_dir=f"{SERIALIZE_COMIC_RESPONSES_DIR}",
            filename=f"{res_dict['num']}.msgpack",
        )
        log.success(
            f"File serialized to: '{SERIALIZE_COMIC_RESPONSES_DIR}/{res_dict['num']}.msgpack"
        )

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception serializing comic #{res_dict['num']}. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc


def _convert_dict_to_xkcdcomic(res_dict: dict = None):
    try:
        comic: XKCDComic = xkcd_mod.response_handler.convert_dict_to_xkcdcomic(
            _dict=res_dict
        )
        log.success(f"Converted response dict to XKCDComic object")
        log.debug(f"XKCDComic object: {comic}")

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception converting dict to XKCDComic. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    return comic


def _request_and_save_comic_img(
    comic: XKCDComic = None,
    cache_transport: hishel.CacheTransport = None,
    output_dir: t.Union[str, Path] = COMIC_IMG_DIR,
) -> XKCDComic:

    img_url: str = comic.img_url
    img_req: httpx.Request = request_client.build_request(url=img_url)

    img_bytes_filename: str = f"{comic.num}.png"
    img_bytes_output_path: Path = Path(f"{output_dir}/{img_bytes_filename}")

    try:
        with request_client.HTTPXController(transport=cache_transport) as httpx_ctl:
            try:
                img_res: httpx.Response = httpx_ctl.send_request(request=img_req)
                if not img_res.status_code == 200:
                    log.warning(
                        f"Non-200 status code: [{img_res.status_code}: {img_res.reason_phrase}]: {img_res.text}"
                    )
                else:
                    log.success(f"Comic image bytes requested")

            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception requesting img bytes. Details: {exc}"
                )
                log.error(msg)
                log.trace(exc)

                raise exc

    except Exception as exc:
        msg = Exception(f"Unhandled exception getting HTTPController. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc

    try:

        img_bytes: bytes = img_res.content
        if not img_bytes_output_path.exists():
            request_client.save_bytes(
                _bytes=img_bytes,
                output_dir=output_dir,
                output_filename=img_bytes_filename,
            )
        else:
            log.warning(
                f"Image has already been saved to path '{img_bytes_output_path}'. Skipping"
            )

        comic.img_bytes = img_bytes

    except Exception as exc:
        msg = Exception(f"Unhandled exception saving img bytes. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc

    return comic


def _serialize_comic_object(
    comic: XKCDComic = None,
    output_dir: t.Union[str, Path] = SERIALIZE_COMIC_OBJECTS_DIR,
    overwrite: bool = False,
) -> None:
    serialized_filename = f"{comic.num}.msgpack"
    output_filepath: Path = Path(f"{output_dir}/{serialized_filename}")

    if output_filepath.exists():
        log.warning(
            f"Comic #{comic.num} is serialized at path '{output_filepath}' already."
        )
        if overwrite:
            log.info(f"overwrite=True, continuing with serialization")
            pass

        else:
            log.warning(f"overwrite=False, skipping.")
            return

    try:
        serialize_utils.serialize_dict(
            data=comic.model_dump(),
            output_dir=output_dir,
            filename=serialized_filename,
            overwrite=overwrite,
        )
        log.success(f"XKCDComic object serialized to '{output_filepath}'.")
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception serializing XKCDComic object. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc


def main(cache_transport: hishel.CacheTransport = None):
    assert cache_transport, ValueError(
        "Missing a cache transport for the request client"
    )
    assert isinstance(cache_transport, hishel.CacheTransport), TypeError(
        f"cache_transport must be a hishel.CacheTransport. Got type: ({type(cache_transport)})"
    )

    res: httpx.Response = _get_current_comic_res(cache_transport=cache_transport)
    res_dict: dict = _get_current_comic_dict_from_res(res=res)
    _serialize_current_comic_dict(res_dict=res_dict)
    comic: XKCDComic = _convert_dict_to_xkcdcomic(res_dict=res_dict)
    comic = _request_and_save_comic_img(
        comic=comic, cache_transport=cache_transport, output_dir=COMIC_IMG_DIR
    )

    log.debug(f"Current comic: {comic}")

    _serialize_comic_object(comic=comic, overwrite=True)


if __name__ == "__main__":
    base_app_setup(settings=settings)
    log.info(f"[TEST][env:{settings.env}|container:{settings.container_env}] App Start")

    CACHE_TRANSPORT: hishel.CacheTransport = request_client.get_cache_transport()

    main(cache_transport=CACHE_TRANSPORT)
