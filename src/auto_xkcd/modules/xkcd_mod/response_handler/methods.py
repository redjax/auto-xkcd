from __future__ import annotations

from pathlib import Path
import typing as t

from core import request_client
from core.paths import SERIALIZE_COMIC_OBJECTS_DIR, SERIALIZE_COMIC_RESPONSES_DIR
from domain.xkcd import XKCDComic
import httpx
from loguru import logger as log
from utils import serialize_utils


def convert_response_to_dict(res: httpx.Response = None) -> dict:
    """Attempt to decode an `httpx.Response` into a dict."""
    assert res, ValueError("Missing an httpx.Response object.")
    assert isinstance(res, httpx.Response), TypeError(
        f"res must be an httpx.Response object. Got type: ({type(res)})"
    )

    with request_client.HTTPXController() as httpx_ctl:
        try:
            comic_dict: dict = httpx_ctl.decode_res_content(res=res)

            return comic_dict

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception decoding comic response bytes. Details: {exc}"
            )
            log.error(msg)

            raise exc


def convert_dict_to_xkcdcomic(_dict: dict = None) -> XKCDComic:
    """Attempt to convert a dict into an XKCDComic object."""
    assert _dict, ValueError("Missing a dict input")
    assert isinstance(_dict, dict), TypeError(
        f"_dict input must be a dict object. Got type: ({type(_dict)})"
    )

    try:
        comic: XKCDComic = XKCDComic.model_validate(_dict)

        return comic

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception converting current comic dict to XKCDComic object. Details: {exc}"
        )
        log.error(msg)

        raise exc


def convert_comic_response_to_xkcdcomic(
    comic_res: httpx.Response = None, serialize_response: bool = True
) -> XKCDComic:
    """Extract Response content to a dict, then validate into an XKCDComic object."""
    ## Convert Response to dict
    try:
        comic_res_dict: dict = convert_response_to_dict(res=comic_res)
        log.success(f"Converted comic #{comic_res_dict['num']} Response to a dict.")
    except Exception as exc:
        msg = Exception(f"Unhandled exception converting comic Response to a dict")
        log.error(msg)
        log.trace(exc)

        raise exc

    if serialize_response:
        ## Save serialized Response
        try:
            serialize_comic_response_dict(res_dict=comic_res_dict)
            log.success(f"Saved serialized comic Response to file")
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception serializing XKCD comic #{comic_res_dict['num']} response dict. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            raise exc

    ## Convert Response dict to XKCDComic
    try:
        comic: XKCDComic = convert_dict_to_xkcdcomic(_dict=comic_res_dict)
        log.success(
            f"Converted comic #{comic.comic_num} Response dict to XKCDComic object"
        )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception converting XKCD comic #{comic.comic_num} response dict to XKCDComic object. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    return comic


def serialize_comic_response_dict(
    res_dict: dict = None,
    output_dir: t.Union[str, Path] = SERIALIZE_COMIC_RESPONSES_DIR,
    overwrite: bool = False,
) -> None:
    serial_file_name: str = f"{res_dict['num']}.msgpack"
    serial_file_path: Path = Path(f"{output_dir}/{serial_file_name}")

    try:
        serialize_utils.serialize_dict(
            data=res_dict,
            output_dir=output_dir,
            filename=serial_file_name,
            overwrite=overwrite,
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
