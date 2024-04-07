import typing as t
from pathlib import Path

from core.request_client import HTTPXController, save_bytes
from core.paths import COMIC_IMG_DIR, SERIALIZE_DIR
from modules import xkcd_mod, data_ctl
from packages.xkcd.comic import get_specific_comic
from utils import serialize_utils

from loguru import logger as log
from red_utils.std import path_utils
import httpx
import hishel


def request_img(
    cache_transport: hishel.CacheTransport = None, img_url: str = None
) -> bytes:
    with HTTPXController(transport=cache_transport) as httpx_ctl:
        req: httpx.Request = httpx_ctl.new_request(url=img_url)
        res: httpx.Response = httpx_ctl.client.send(request=req)

    img_bytes: bytes = res.content

    return img_bytes


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
            img_bytes: bytes = request_img(
                cache_transport=cache_transport, img_url=comic.img_url
            )
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception requesting comic #{comic.num} image bytes. Details: {exc}"
            )
            log.error(msg)
            log.trace(msg)

            raise exc

    else:
        ## Found comic.img_url, request img bytes
        img_bytes: bytes = request_img(
            cache_transport=cache_transport, img_url=comic.img_url
        )

    _saved: bool = save_bytes(
        img_bytes=img_bytes, output_dir=output_dir, output_filename=output_filename
    )
    if not _saved:
        log.warning(f"Could not save image for comic #{comic.num}")
        return False

    return True
