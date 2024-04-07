from core import request_client
from domain.xkcd import XKCDComic
from core import request_client

import httpx
from loguru import logger as log


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
