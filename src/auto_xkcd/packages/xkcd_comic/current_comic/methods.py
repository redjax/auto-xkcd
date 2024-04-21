import typing as t
from pathlib import Path
from sqlalchemy.exc import IntegrityError
import sqlite3 as sqlite

from core.config import settings, db_settings
from core import database, request_client
from core import paths
from core.dependencies import get_db
from helpers.validators import validate_hishel_cachetransport
from helpers import data_ctl
from modules import xkcd_mod, data_mod, requests_prefab
from domain.xkcd import comic

from loguru import logger as log
import httpx
import hishel
from red_utils.ext.time_utils import get_ts


def get_current_comic(
    cache_transport: hishel.CacheTransport = request_client.get_cache_transport(),
) -> comic.XKCDComic:
    cache_transport = validate_hishel_cachetransport(cache_transport)

    ## Build request
    req: httpx.Request = requests_prefab.current_comic_req()

    ## Make request for current comic
    try:
        log.info("Requesting current XKCD comic")
        comic_res: httpx.Response = xkcd_mod.make_comic_request(
            cache_transport=cache_transport, request=req
        )
        log.debug(f"Current comic: {comic_res}")
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception making request for current XKCD comic. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    ## Parse httpx.Response into comic.XKCDComic
    try:
        # comic_obj: comic.XKCDComic = _parse_res_to_comic(response=res)
        comic_obj: comic.XKCDComic = (
            xkcd_mod.response_handler.convert_comic_response_to_xkcdcomic(
                comic_res=comic_res
            )
        )

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception parsing current XKCD comic Response to XKCDComic object. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    ## Update current comic metadata JSON
    try:
        current_comic_meta: comic.CurrentComicMeta = xkcd_mod.update_current_comic_json(
            comic_obj=comic_obj
        )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception updating current_comic.json file. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        log.warning(f"current_comic.json file not updated.")

    ## Update current comic metadata in database
    try:
        xkcd_mod.update_current_comic_meta_db(current_comic_meta=current_comic_meta)
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception updating current comic metadata in database. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        log.warning(f"Current comic metadata not updated in database")

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

    return comic_obj
