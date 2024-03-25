import typing as t
from pathlib import Path

from core import request_client, COMIC_IMG_DIR
from modules import xkcd_mod
from packages.xkcd.helpers import extract_img_bytes, parse_comic_response

import httpx
import hishel
from loguru import logger as log


def save_img(
    comic: t.Union[httpx.Response, xkcd_mod.XKCDComic],
    output_dir: t.Union[str, Path] = COMIC_IMG_DIR,
    output_filename: str = None,
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
        comic_dict: dict = parse_comic_response(res=comic)
        _comic: xkcd_mod.XKCDComic = xkcd_mod.XKCDComic.model_validate(comic_dict)

        comic = _comic

    assert output_dir, ValueError("Missing output directory path")
    assert isinstance(output_dir, str) or isinstance(output_dir, Path), TypeError(
        f"output_dir must be a str or Path. Got type: ({type(output_dir)})"
    )
    if isinstance(output_dir, Path):
        if "~" in f"{output_dir}":
            _dir = output_dir.expanduser()
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

    if isinstance(comic, httpx.Response):
        img_bytes: bytes = extract_img_bytes(res=comic)
    elif isinstance(comic, xkcd_mod.XKCDComic):
        req: httpx.Request = xkcd_mod.make_req(url=comic.img_url)

        try:
            res: httpx.Response = request_client.simple_get(request=req)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception requesting comic #{comic.comic_num} image. Details: {exc}"
            )
            log.error(msg)

            raise msg

        img_bytes: bytes = extract_img_bytes(res=res)

    log.debug(f"Saving image bytes.")
    try:
        with open(output_path, "wb") as f:
            f.write(img_bytes)
            log.success(f"Image saved to path '{output_path}'")
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception saving image to path '{output_path}'. Details: {exc}"
        )
        log.error(msg)

        raise msg
