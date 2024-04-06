import typing as t
from pathlib import Path

from core.request_client import HTTPXController
from core.paths import COMIC_IMG_DIR
from modules import xkcd_mod

from loguru import logger as log
from red_utils.std import path_utils
import httpx
import hishel


def get_saved_imgs(
    comic_img_dir: t.Union[str, Path] = COMIC_IMG_DIR, as_int: bool = True
) -> list[str] | list[int]:
    assert comic_img_dir, ValueError("Missing comic_img_dir")
    assert isinstance(comic_img_dir, str) or isinstance(comic_img_dir, Path), TypeError(
        f"comic_img_dir must be a string or Path. Got type: ({type(comic_img_dir)})"
    )
    if isinstance(comic_img_dir, str):
        if "~" in comic_img_dir:
            comic_img_dir: Path = Path(comic_img_dir).expanduser()
        else:
            comic_img_dir: Path = Path(comic_img_dir)
    if isinstance(comic_img_dir, Path):
        if "~" in f"{comic_img_dir}":
            comic_img_dir: Path = comic_img_dir.expanduser()

    if not comic_img_dir.exists():
        log.warning(f"Comic image directory '{comic_img_dir}' does not exist.")
        return

    _imgs: list[Path] = path_utils.scan_dir(
        target=comic_img_dir, as_pathlib=True, return_type="files"
    )
    # log.debug(f"_imgs ({type(_imgs)}): {_imgs}")

    if as_int:
        int_list: list[int] = []

        for img in _imgs:
            img_stripped: str = img.stem
            img_int = int(img_stripped)
            int_list.append(img_int)

        return sorted(int_list)

    return _imgs


def request_img(
    cache_transport: hishel.CacheTransport = None, img_url: str = None
) -> bytes:
    with HTTPXController(transport=cache_transport) as httpx_ctl:
        req: httpx.Request = httpx_ctl.new_request(url=img_url)
        res: httpx.Response = httpx_ctl.client.send(request=req)

    img_bytes: bytes = res.content

    return img_bytes


def save_bytes(
    img_bytes: bytes = None,
    output_dir: t.Union[str, Path] = None,
    output_filename: str = None,
):
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

    output_path: Path = Path(f"{output_dir}/{output_filename}")
    if not output_path.parent.exists():
        log.warning(
            f"Parent directory '{output_path.parent}' does not exist. Creating."
        )
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception creating directory '{output_path.parent}'. Details: {exc}"
            )
            log.error(msg)

            raise msg

    # log.debug(f"Saving image bytes.")
    try:
        with open(output_path, "wb") as f:
            f.write(img_bytes)
            log.success(f"Image saved to path '{output_path}'")

        return True
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception saving image to path '{output_path}'. Details: {exc}"
        )
        log.error(msg)

        # raise msg

        return False


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

        comic = _comic
    if isinstance(comic, dict):
        log.warning(f"Input comic is a dict. Converting to XKCDComic instance.")
        _comic: xkcd_mod.XKCDComic = xkcd_mod.XKCDComic.model_validate(comic)
        comic = _comic

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
        saved_imgs: list[int] = get_saved_imgs()
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
        log.warning(
            f"Image URL for comic #{comic.num}' is None. Requesting comic #{comic.num} to get image URL"
        )

    img_bytes: bytes = request_img(
        cache_transport=cache_transport, img_url=comic.img_url
    )
    _saved = save_bytes(
        img_bytes=img_bytes, output_dir=output_dir, output_filename=output_filename
    )
    if not _saved:
        log.warning(f"Could not save image for comic #{comic.num}")
        return False

    return True
