from core import ENSURE_DIRS, settings
from core.request_client import simple_get
from packages import xkcd
from modules import xkcd_mod
import json

import httpx
from red_utils.std import path_utils
from red_utils.ext.loguru_utils import init_logger, sinks
from loguru import logger as log

if __name__ == "__main__":
    settings.log_level = "DEBUG"

    init_logger(sinks=[sinks.LoguruSinkStdOut(level=settings.log_level).as_dict()])

    path_utils.ensure_dirs_exist(ENSURE_DIRS)

    _comic_num = 24

    try:
        comic_res: httpx.Response = xkcd.get_comic(comic_num=_comic_num)
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception requesting comic #{_comic_num}. Details: {exc}"
        )
        log.error(msg)

        raise msg

    try:
        comic_dict = xkcd.helpers.parse_comic_response(res=comic_res)
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception parsing comic response to dict. Details: {exc}"
        )
        log.error(msg)

        raise msg

    try:
        comic: xkcd_mod.XKCDComic = xkcd_mod.XKCDComic.model_validate(comic_dict)
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception converting comic reponse dict to xkcd_mod.XKCDComic. Details: {exc}"
        )
        log.error(msg)

        raise msg

    try:
        xkcd.save_img(comic=comic_res, output_filename=f"{comic.comic_num}.png")
    except Exception as exc:
        msg = Exception(f"Unhandled exception saving image. Details: {exc}")
        log.error(msg)

        raise msg
