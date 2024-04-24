from pathlib import Path

from domain.xkcd.comic.schemas import XKCDComicImage, XKCDComic
from modules import requests_prefab, xkcd_mod
from packages import xkcd_comic
from core import get_db
from helpers import data_ctl

from loguru import logger as log
from fastapi import status
from fastapi.responses import JSONResponse


def search_comic_img(comic_num: int = None) -> bytes | None:
    log.info(f"Searching database for XKCD comic #{comic_num}")
    try:
        ## Check database for comic img bytes first
        db_comic: XKCDComicImage | None = xkcd_comic.comic_img.retrieve_img_from_db(
            comic_num=comic_num
        )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception searching database for XKCD comic #{comic_num}. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        log.warning(
            f"Error while searching database for XKCD comic #{comic_num}. Searching local image files."
        )

    if db_comic:
        log.debug(f"Found comic image. ({type(db_comic)})")
        log.info(f"Found image for XKCD comic #{comic_num} in database.")

        log.info(f"Returning comic image")
        try:
            return db_comic.img
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception getting Response object. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            log.warning(
                f"Image found in database for XKCD comic #{comic_num}, but an error prevented returning it directly. Continuing to search from filesystem"
            )
    else:
        log.warning(f"Did not find image for XKCD comic #{comic_num} in database.")

    log.info(f"Searching local image files for XKCD comic #{comic_num}.")

    ## Get image file
    try:
        img_file: Path | None = xkcd_comic.comic_img.lookup_img_file(
            comic_num=comic_num
        )

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting image for XKCD comic #{comic_num}. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    if img_file:
        log.info(f"Found image file at path '{img_file}'. Loading to bytestring")
        try:
            with open(img_file, "rb") as _img:
                contents: bytes = _img.read()

            return contents

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception reading contents of file '{img_file}'. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            raise exc
    else:
        log.warning(
            f"Did not find image file saved locally for XKCD comic #{comic_num}. Requesting comic from XKCD API"
        )

        try:
            _comic: XKCDComic | None = xkcd_comic.comic.get_single_comic(
                comic_num=comic_num
            )

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception requesting XKCD comic #{comic_num}. Details: {exc}"
            )

        if _comic:
            log.debug(f"Retrieved XKCD comic #{comic_num}: {_comic}")

            try:
                img_bytes: bytes = xkcd_comic.comic_img.request_img_from_api(
                    comic_obj=_comic
                )

                return img_bytes

            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception requesting XKCD comic #{comic_num} from XKCD's API. Details: {exc}"
                )
                log.error(msg)
                log.trace(exc)

    return None
