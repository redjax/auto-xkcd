from __future__ import annotations

from pathlib import Path
import sqlite3 as sqlite
import typing as t

from core import IGNORE_COMIC_NUMS, database, paths, request_client
from core.config import db_settings, settings
from core.constants import XKCD_URL_BASE, XKCD_URL_POSTFIX
from core.dependencies import get_db
from domain.xkcd import comic
from helpers import data_ctl
from helpers.validators import validate_hishel_cachetransport
import hishel
import httpx
from loguru import logger as log
from modules import data_mod, requests_prefab, xkcd_mod
from red_utils.ext.time_utils import get_ts
from sqlalchemy.exc import IntegrityError

def get_single_comic(
    cache_transport: hishel.CacheTransport = request_client.get_cache_transport(),
    comic_num: int = None,
    save_serial: bool = True,
    overwrite: bool = True,
) -> comic.XKCDComic | None:
    """Request a single XKCD comic by its comic number.

    Params:
        cache_transport (hishel.CacheTransport): A cache transport for the request client.
        comic_num (int): The number of the XKCD comic strip to request.

    Returns:
        (XKCDComic): The specified XKCD comic.

    """
    cache_transport = validate_hishel_cachetransport(cache_transport=cache_transport)

    if comic_num in IGNORE_COMIC_NUMS:
        log.warning(f"Comic #{comic_num} is in list of ignored comic numbers. Skipping")

        return None

    req: httpx.Request = requests_prefab.comic_num_req(comic_num=comic_num)

    ## Get comic Response
    try:
        comic_res: httpx.Response = xkcd_mod.make_comic_request(
            cache_transport=cache_transport, request=req
        )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting comic #{comic_num}. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    if comic_res.status_code == 404:
        err_comic_url: str = f"{XKCD_URL_BASE}/{comic_num}"
        log.warning(
            f"Could not find comic #{comic_num}. Does this comic exist? Check the XKCD site: {err_comic_url}"
        )

        return None

    ## Convert httpx.Response into XKCDComic object
    try:
        comic_obj: comic.XKCDComic = (
            xkcd_mod.response_handler.convert_comic_response_to_xkcdcomic(
                comic_res=comic_res
            )
        )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception converting httpx.Response to XKCDComic object. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    if save_serial:
        ## Serialize comic object
        try:
            xkcd_mod.save_serialize_comic_object(comic=comic_obj, overwrite=overwrite)
            log.success(f"Serialized XKCD comic #{comic_obj.comic_num}")
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception serializing XKCD comic #{comic_obj.comic_num}. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            raise exc

    ## Update comic_nums.txt file
    log.debug(f"Updating comic_nums.txt file")
    try:
        data_ctl.update_comic_nums_file(comic_num=comic_obj.comic_num)
    except Exception as exc:
        msg = Exception(f"Unhandled exception updating comic_nums file. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc

    ## Save comic image to file
    try:
        comic_image: comic.XKCDComicImage = xkcd_mod.save_comic_img(
            cache_transport=cache_transport, comic_obj=comic_obj
        )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception saving image for XKCD comic #{comic_obj.comic_num}. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)
        log.warning(f"Did not save image for XKCD comic #{comic_obj.comic_num}")

    ## Save comic image to db
    try:
        db_comic_image: comic.XKCDComicImage = xkcd_mod.save_comic_img_to_db(
            comic_img=comic_image
        )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception saving image for comic #{comic_obj.comic_num} to database. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)
        log.warning(f"Did not save image to database for comic #{comic_obj.comic_num}")

    ## Save comic to database
    try:
        comic_obj = xkcd_mod.save_comic_to_db(comic_obj=comic_obj)
    except IntegrityError as integ_err:
        msg = Exception(f"Comic #{comic_obj.comic_num} already exists in database.")
        log.warning(msg)

        pass
    except Exception as exc:
        if isinstance(exc, sqlite.IntegrityError) or isinstance(
            exc,
        ):
            pass
        else:
            msg = Exception(
                f"Unhandled exception saving XKCD comic #{comic_obj.comic_num} to database. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)
            log.warning(f"Did not save XKCD comic #{comic_obj.comic_num} to database.")

    log.debug(f"Comic #{comic_obj.comic_num}: {comic_obj}")
    return comic_obj
