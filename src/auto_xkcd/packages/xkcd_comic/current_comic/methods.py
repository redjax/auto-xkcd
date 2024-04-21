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


def _make_request(
    cache_transport: hishel.CacheTransport = request_client.get_cache_transport(),
    request: httpx.Request = None,
) -> httpx.Response:
    cache_transport = validate_hishel_cachetransport(cache_transport)

    try:
        with request_client.HTTPXController(transport=cache_transport) as httpx_ctl:
            try:
                res: httpx.Response = httpx_ctl.send_request(request=request)
                log.debug(
                    f"[URL: {request.url}]: [{res.status_code}: {res.reason_phrase}]"
                )

                return res
            except Exception as exc:
                msg = Exception(f"Unhandled exception making request. Details: {exc}")
                log.error(msg)
                log.trace(exc)

                raise exc
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception initializing HTTPXController. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc


def _parse_res_to_comic(response: httpx.Response = None) -> comic.XKCDComic:
    comic_obj: comic.XKCDComic = (
        xkcd_mod.response_handler.convert_comic_response_to_xkcdcomic(
            comic_res=response
        )
    )

    return comic_obj


def _save_comic_img(
    cache_transport: hishel.CacheTransport = request_client.get_cache_transport(),
    comic_obj: comic.XKCDComic = None,
):
    cache_transport = validate_hishel_cachetransport(cache_transport)

    try:
        saved_comic: comic.XKCDComic = xkcd_mod.request_and_save_comic_img(
            comic=comic_obj, cache_transport=cache_transport
        )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception saving image for XKCD comic #{comic_obj.comic_num}. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc


def _save_comic_to_db(
    comic_obj: comic.XKCDComic = None, exclude_fields: dict = {"comic_num_hash"}
) -> comic.XKCDComic:
    try:
        db_model: comic.XKCDComicModel = comic.XKCDComicModel(**comic_obj.model_dump())
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception building XKCDComicModel from input XKCDComic object. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    try:
        with get_db() as session:
            repo = comic.XKCDComicRepository(session=session)

            try:
                repo.add(entity=db_model)

                comic_obj.img_saved = True

                return comic_obj
            except IntegrityError as integ_err:
                msg = Exception(
                    f"Comic #{comic_obj.comic_num} already exists in database."
                )
                log.warning(msg)

                comic_obj.img_saved = True

                return comic_obj
            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception writing XKCD comic #{comic_obj.comic_num} to database. Details ({type(exc)}): {exc}"
                )
                log.error(msg)
                log.trace(exc)

                raise exc
    except IntegrityError or sqlite.IntegrityError as integ_err:
        comic_obj.img_saved = True
        return comic_obj
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting database connection. Details ({type(exc)}): {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc


def _update_current_comic_json(
    current_comic_json_file: str = paths.CURRENT_COMIC_FILE,
    comic_obj: comic.XKCDComic = None,
):
    update_ts = get_ts()
    current_comic_meta: comic.CurrentComicMeta = comic.CurrentComicMeta(
        last_updated=update_ts, comic_num=comic_obj.comic_num
    )

    data_ctl.update_current_comic_meta(
        current_comic_file=current_comic_json_file, current_comic=current_comic_meta
    )


def get_current_comic(
    cache_transport: hishel.CacheTransport = request_client.get_cache_transport(),
) -> comic.XKCDComic:
    cache_transport = validate_hishel_cachetransport(cache_transport)

    ## Build request
    req: httpx.Request = requests_prefab.current_comic_req()

    ## Make request for current comic
    try:
        log.info("Requesting current XKCD comic")
        res: httpx.Response = _make_request(
            cache_transport=cache_transport, request=req
        )
        log.debug(f"Current comic: {res}")
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception making request for current XKCD comic. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    ## Parse httpx.Response into comic.XKCDComic
    try:
        comic_obj: comic.XKCDComic = _parse_res_to_comic(response=res)

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception parsing current XKCD comic Response to XKCDComic object. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    ## Update current comic metadata JSON
    try:
        _update_current_comic_json(comic_obj=comic_obj)
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception updating current_comic.json file. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        log.warning(f"current_comic.json file not updated.")

    ## Save comic image to file
    try:
        _save_comic_img(cache_transport=cache_transport, comic_obj=comic_obj)
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception saving image for XKCD comic #{comic_obj.comic_num}. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)
        log.warning(f"Did not save image for XKCD comic #{comic_obj.comic_num}")

    ## Save comic to database
    try:
        comic_obj = _save_comic_to_db(comic_obj=comic_obj)
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
