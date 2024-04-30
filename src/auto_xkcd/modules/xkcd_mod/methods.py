from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path
import sqlite3
import typing as t

from .response_handler import convert_db_comic_to_comic_obj

from core import paths, request_client
from core.constants import XKCD_URL_BASE
from core.dependencies import get_db
from domain.xkcd import comic
from helpers import data_ctl
from helpers.validators import validate_hishel_cachetransport, validate_path
import hishel
import httpx
from loguru import logger as log
import msgpack
from red_utils.ext.time_utils import get_ts
from sqlalchemy.exc import IntegrityError
import sqlalchemy.orm as sa
from utils import serialize_utils


def make_comic_request(
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


def save_comic_img(
    cache_transport: hishel.CacheTransport = request_client.get_cache_transport(),
    comic_obj: comic.XKCDComic = None,
) -> comic.XKCDComicImage:
    cache_transport = validate_hishel_cachetransport(cache_transport)

    try:
        saved_comic: bytes = request_and_save_comic_img(
            comic=comic_obj, cache_transport=cache_transport
        )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception saving image for XKCD comic #{comic_obj.comic_num}. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    comic_image: comic.XKCDComicImage = comic.XKCDComicImage(
        comic_num=comic_obj.comic_num, img=saved_comic
    )

    return comic_image


def save_comic_to_db(
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
    except IntegrityError or sqlite3.IntegrityError as integ_err:
        comic_obj.img_saved = True
        return comic_obj
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting database connection. Details ({type(exc)}): {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc


def get_comic_from_db(comic_num: int = None) -> None | comic.XKCDComic:
    try:
        with get_db() as session:
            repo = comic.XKCDComicRepository(session=session)

            try:
                db_comic: comic.XKCDComicModel = repo.get_by_num(num=comic_num)
            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception writing XKCD comic #{comic_num} to database. Details ({type(exc)}): {exc}"
                )
                log.error(msg)
                log.trace(exc)

                return None
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting database connection. Details ({type(exc)}): {exc}"
        )
        log.error(msg)
        log.trace(exc)

        return None

    if db_comic is None:
        return None
    else:
        try:
            _comic: comic.XKCDComic = convert_db_comic_to_comic_obj(db_comic=db_comic)

            return _comic
        except Exception as exc:
            msg = Exception(
                f"Error converting XKCDComicModel to XKCDComic object. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            raise exc


def update_current_comic_json(
    current_comic_json_file: str = paths.CURRENT_COMIC_FILE,
    comic_obj: comic.XKCDComic = None,
) -> comic.CurrentComicMeta:
    update_ts = get_ts()
    current_comic_meta: comic.CurrentComicMeta = comic.CurrentComicMeta(
        last_updated=update_ts, comic_num=comic_obj.comic_num
    )

    try:
        data_ctl.update_current_comic_meta(
            current_comic_file=current_comic_json_file, current_comic=current_comic_meta
        )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception updating '{current_comic_json_file}'. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)
        log.warning(f"File '{current_comic_json_file}' not updated.")

    return current_comic_meta


def update_current_comic_meta_db(
    current_comic_meta: comic.CurrentComicMeta = None,
) -> comic.CurrentComicMeta:
    try:
        db_model: comic.CurrentComicMetaModel = comic.CurrentComicMetaModel(
            **current_comic_meta.model_dump()
        )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception dumping CurrentComicMeta object to database model. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    try:
        with get_db() as session:
            repo = comic.CurrentComicMetaRepository(session=session)

            try:
                repo.add_or_update(entity=db_model)

                return current_comic_meta
            except IntegrityError as integ_err:
                msg = Exception(f"Current comic metadata already exists in database.")
                log.warning(msg)

                # return current_comic_meta
                raise integ_err
            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception writing current comic metadata to database. Details ({type(exc)}): {exc}"
                )
                log.error(msg)
                log.trace(exc)

                raise exc
    except IntegrityError or sqlite3.IntegrityError as integ_err:
        # return current_comic_meta
        raise integ_err
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting database connection. Details ({type(exc)}): {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc


def save_comic_img_to_db(comic_img: comic.XKCDComicImage = None):
    try:
        db_model: comic.XKCDComicImageModel = comic.XKCDComicImageModel(
            **comic_img.model_dump()
        )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception building XKCDComicImageModel from input XKCDComicImage object. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    try:
        with get_db() as session:
            repo = comic.XKCDComicImageRepository(session=session)

            try:
                repo.add(entity=db_model)

                return comic_img
            except IntegrityError as integ_err:
                msg = Exception(
                    f"Comic #{comic_img.comic_num} already exists in database."
                )
                log.warning(msg)

                return comic_img
            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception writing XKCD comic #{comic_img.comic_num} to database. Details ({type(exc)}): {exc}"
                )
                log.error(msg)
                log.trace(exc)

                raise exc
    except IntegrityError or sqlite3.IntegrityError as integ_err:
        return comic_img
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting database connection. Details ({type(exc)}): {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc


def request_and_save_comic_img(
    comic: comic.XKCDComic = None,
    cache_transport: hishel.CacheTransport = None,
    output_dir: t.Union[str, Path] = paths.COMIC_IMG_DIR,
) -> bytes:
    """Request a specific comic's image given an input `XKCDComic` object.

    Params:
        comic (XKCDComic): An initialized `XKCDComic` object.
        cache_transport (hishel.CacheTransport): A cache transport for the request client.
        output_dir (str|Path): Path to the directory where comic image will be saved.

    """
    log.debug(f"Comic ({type(comic)}): {comic}")
    ## Extract image URL
    img_url: str = comic.img_url
    if img_url is None:
        log.warning(
            f"URL for comic #{comic.comic_num} is None. Setting URL to {XKCD_URL_BASE}/{comic.comic_num}"
        )
        url: str = f"{XKCD_URL_BASE}/{comic.comic_num}"

    ## Build request for image
    img_req: httpx.Request = request_client.build_request(url=img_url)

    img_bytes_filename: str = f"{comic.comic_num}.png"
    img_bytes_output_path: Path = Path(f"{output_dir}/{img_bytes_filename}")

    try:
        with request_client.HTTPXController(transport=cache_transport) as httpx_ctl:
            try:
                img_res: httpx.Response = httpx_ctl.send_request(request=img_req)
                if not img_res.status_code == 200:
                    log.warning(
                        f"Non-200 status code: [{img_res.status_code}: {img_res.reason_phrase}]: {img_res.text}"
                    )
                else:
                    log.success(f"Comic image bytes requested")

            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception requesting img bytes. Details: {exc}"
                )
                log.error(msg)
                log.trace(exc)

                raise exc

    except Exception as exc:
        msg = Exception(f"Unhandled exception getting HTTPController. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc

    try:

        img_bytes: bytes = img_res.content
        if not img_bytes_output_path.exists():
            request_client.save_bytes(
                _bytes=img_bytes,
                output_dir=output_dir,
                output_filename=img_bytes_filename,
            )
        else:
            log.warning(
                f"Image has already been saved to path '{img_bytes_output_path}'. Skipping"
            )

    except Exception as exc:
        msg = Exception(f"Unhandled exception saving img bytes. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc

    return img_bytes


def load_serialized_comic(
    serialize_dir: t.Union[str, Path] = paths.SERIALIZE_COMIC_OBJECTS_DIR,
    comic_num: int = None,
) -> comic.XKCDComic | None:
    """Load a serialized XKCDComic object from a file.

    Params:
        serialize_dir (str|Path): Path to directory containing serialized XKCDComic objects.
        comic_num (int): Number of comic to load.

    """
    serialized_comic_filename: str = f"{comic_num}.msgpack"
    serialized_comic_path: Path = Path(f"{serialize_dir}/{serialized_comic_filename}")

    if not serialized_comic_path.exists():
        log.warning(
            f"Could not find serialized comic at path '{serialized_comic_path}'."
        )

        return

    log.debug(f"Loading serialized comic from file '{serialized_comic_path}'.")
    try:
        with open(serialized_comic_path, "rb") as f:
            data = f.read()
            deserialized: dict = msgpack.unpackb(data)
            log.success(f"Deserialized file contents into dict")

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception deserializing comic data in file '{serialized_comic_path}'. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        return None

    log.debug(f"Converting serialized data dict to XKCDComic object")
    try:
        _comic: comic.XKCDComic = comic.XKCDComic.model_validate(deserialized)
        log.success(
            f"Comic #{comic_num} serialized object restored to XKCDComic object."
        )

        return _comic
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception validating serialized dict into XKCDComic object. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        return None


def save_serialize_comic_object(
    comic: comic.XKCDComic = None,
    output_dir: t.Union[str, Path] = paths.SERIALIZE_COMIC_OBJECTS_DIR,
    overwrite: bool = False,
) -> None:
    """Save an `XKCDComic` object to a `.msgpack` file.

    Params:
        comic (XKCDComic): An instantiated `XKCDComic` object.
        output_dir (str|Path): The directory where the serialized file will be saved. Note: the filename will be generated
            during function execution, you should not include the filename in this path.
        overwrite (bool): If `True`, file will be overwritten if it already exists.

    """
    serialized_filename = f"{comic.comic_num}.msgpack"
    output_filepath: Path = Path(f"{output_dir}/{serialized_filename}")

    if output_filepath.exists():
        log.warning(
            f"Comic #{comic.comic_num} is serialized at path '{output_filepath}' already."
        )
        if overwrite:
            # log.info(f"overwrite=True, continuing with serialization")
            pass

        else:
            # log.warning(f"overwrite=False, skipping.")

            return

    try:
        serialize_utils.serialize_dict(
            data=comic.model_dump(),
            output_dir=output_dir,
            filename=serialized_filename,
            overwrite=overwrite,
        )
        log.success(f"XKCDComic object serialized to '{output_filepath}'.")
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception serializing XKCDComic object. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc


def list_missing_nums() -> list[int]:
    """Compile a list of missing XKCD comic numbers."""
    try:
        current_comic_meta: comic.CurrentComicMeta = data_ctl.read_current_comic_meta()
        current_comic_num: int = current_comic_meta.comic_num
        # log.debug(f"Current comic number: {current_comic_num}")
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception reading current comic metadata. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    all_comic_nums: list[int] = list(range(1, current_comic_num))

    try:
        saved_comic_nums: list[int] = data_ctl.get_saved_imgs()
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception loading saved comic numbers. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    missing_comic_nums: list[int] = [
        num for num in all_comic_nums if num not in saved_comic_nums
    ]
    log.debug(f"Found [{len(missing_comic_nums)}] missing comic number(s)")

    return missing_comic_nums


# @lru_cache
def count_comics_in_db() -> int:
    with get_db() as session:
        repo = comic.XKCDComicRepository(session)

        _count = repo.count()

    return _count


def encode_img_bytes(img_bytes: bytes = None, encoding: str = "utf-8"):
    img_base64: str = base64.b64encode(img_bytes).decode(encoding=encoding)

    return img_base64


def read_current_comic_file() -> int:
    try:
        with data_ctl.CurrentComicController() as current_comic_ctl:
            _data = current_comic_ctl.read()

            return _data

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception reading current comic metadata. Details: {exc}"
        )
        log.error(msg)

        ## Default to 0, which is the "current" XKCD comic
        return None
