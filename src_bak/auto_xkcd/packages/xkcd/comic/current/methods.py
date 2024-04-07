from __future__ import annotations

import json
from pathlib import Path
import typing as t

from .json_encoders import DateTimeEncoder

from core.paths import CURRENT_COMIC_FILE
from loguru import logger as log
from modules import xkcd_mod

def validate_current_comic_file(current_comic_file: t.Union[str, Path] = None) -> Path:
    assert current_comic_file, ValueError("Missing current comic details file")
    assert isinstance(current_comic_file, str) or isinstance(
        current_comic_file, Path
    ), TypeError(
        f"current_comic_file must be a str or Path. Got type: ({type(current_comic_file)})"
    )
    if isinstance(current_comic_file, str):
        current_comic_file: Path = Path(current_comic_file)
    if "~" in f"{current_comic_file}":
        current_comic_file = current_comic_file.expanduser()

    if not current_comic_file.exists():
        log.warning(
            f"Current comic file does not exist: '{current_comic_file}'. Creating empty file."
        )

        try:
            data: dict[str, t.Union[str, None]] = {
                "comic_num": None,
                "last_updated": None,
            }

            ## Save to file
            with open(file=current_comic_file, mode="w") as f:
                json.dump(obj=data, fp=f)

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception writing default dict to file '{current_comic_file}'. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

    return current_comic_file


def read_current_comic_meta(
    current_comic_file: t.Union[str, Path] = CURRENT_COMIC_FILE
) -> xkcd_mod.CurrentComicMeta:

    try:
        current_comic_file = validate_current_comic_file(current_comic_file)
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception validating current_comic_file ({type(current_comic_file)}). Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    assert current_comic_file.exists(), FileNotFoundError(
        f"Could not find metadata file: {current_comic_file}"
    )

    try:
        with open(current_comic_file, "r") as f:
            _data = json.load(f)
            # log.debug(f"Current comic metadata ({type(_data)}): {_data}")

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception reading current comic metadata file: {current_comic_file}. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    try:
        _metadata: xkcd_mod.CurrentComicMeta = xkcd_mod.CurrentComicMeta.model_validate(
            obj=_data
        )

        return _metadata

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception converting comic metadata dict to CurrentComicMeta object. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc


def update_current_comic_meta(
    current_comic_file: t.Union[str, Path] = CURRENT_COMIC_FILE,
    current_comic: xkcd_mod.CurrentComicMeta = None,
) -> bool:
    current_comic_file = validate_current_comic_file(current_comic_file)
    assert current_comic, ValueError("Missing CurrentComicMeta object")

    current_comic.overwrite_last_updated()

    try:
        _data = current_comic.model_dump()
    except Exception as exc:
        msg = Exception(f"Unhandled exception dumping model. Details: {exc}")

    log.debug(f"Saving current comic metadata: {_data}")

    try:
        with open(current_comic_file, "w") as f:
            # json.dump(_json, f)
            json.dump(
                obj=_data,
                indent=4,
                sort_keys=True,
                cls=DateTimeEncoder,
                default=str,
                fp=f,
            )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception saving updated current comic metadata. Details: {exc}"
        )
        log.error(msg)
        log.trace(msg)

        raise exc