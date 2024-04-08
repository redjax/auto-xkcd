import typing as t
from pathlib import Path

from core import request_client
from core.paths import (
    COMIC_IMG_DIR,
    SERIALIZE_COMIC_OBJECTS_DIR,
    SERIALIZE_COMIC_RESPONSES_DIR,
)
from domain.xkcd.comic import XKCDComic, CurrentComicMeta
from utils import serialize_utils
from helpers import data_ctl

import hishel
import httpx
from loguru import logger as log
import msgpack


def request_and_save_comic_img(
    comic: XKCDComic = None,
    cache_transport: hishel.CacheTransport = None,
    output_dir: t.Union[str, Path] = COMIC_IMG_DIR,
) -> XKCDComic:

    img_url: str = comic.img_url
    img_req: httpx.Request = request_client.build_request(url=img_url)

    img_bytes_filename: str = f"{comic.num}.png"
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

        comic.img_bytes = img_bytes

    except Exception as exc:
        msg = Exception(f"Unhandled exception saving img bytes. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc

    return comic


def load_serialized_comic(
    serialize_dir: t.Union[str, Path] = SERIALIZE_COMIC_OBJECTS_DIR,
    comic_num: int = None,
) -> XKCDComic | None:
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
        comic: XKCDComic = XKCDComic.model_validate(deserialized)
        log.success(
            f"Comic #{comic_num} serialized object restored to XKCDComic object."
        )

        return comic
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception validating serialized dict into XKCDComic object. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        return None


def save_serialize_comic_object(
    comic: XKCDComic = None,
    output_dir: t.Union[str, Path] = SERIALIZE_COMIC_OBJECTS_DIR,
    overwrite: bool = False,
) -> None:
    serialized_filename = f"{comic.num}.msgpack"
    output_filepath: Path = Path(f"{output_dir}/{serialized_filename}")

    if output_filepath.exists():
        log.warning(
            f"Comic #{comic.num} is serialized at path '{output_filepath}' already."
        )
        if overwrite:
            log.info(f"overwrite=True, continuing with serialization")
            pass

        else:
            log.warning(f"overwrite=False, skipping.")
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


def list_missing_nums():
    try:
        current_comic_meta: CurrentComicMeta = data_ctl.read_current_comic_meta()
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
