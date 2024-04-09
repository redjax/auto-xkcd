from __future__ import annotations

import json
from pathlib import Path
import typing as t

from core import request_client
from core.paths import COMIC_IMG_DIR, CURRENT_COMIC_FILE, DATA_DIR, SERIALIZE_DIR
from domain.xkcd import CurrentComicMeta
from loguru import logger as log
from red_utils.std import path_utils


def update_comic_nums_file(
    file: t.Union[str, Path] = Path(f"{DATA_DIR}/comic_nums.txt"), comic_num: int = None
) -> None:
    """Update/add to a `.txt` file tracking XKCD comics successfully requested.

    Params:
        file (str|Path): Path to a `comic_nums.txt` file to update.
        comic_num (int): The comic number to add (if it does not exist).

    """
    assert comic_num is not None, ValueError("Missing comic number")
    assert isinstance(comic_num, int), TypeError(f"comic_num must be an integer")

    assert isinstance(file, str) or isinstance(file, Path), TypeError(
        f"file must be a string or Path object. Got type: ({type(file)})"
    )
    if isinstance(file, str):
        file = Path(file)
    if "~" in str(file):
        file = file.expanduser()

    if not file.parent.exists():
        try:
            file.parent.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception creating directory '{file.parent}'. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)
            raise exc

    if not file.exists():
        file.touch()

    with open(file=file, mode="r") as f:
        lines: list[str] = f.readlines()
        comic_nums: list[int] = []
        for line in lines:
            stripped_line: str = line.strip()
            if stripped_line:
                comic_nums.append(int(stripped_line))

    if comic_num not in comic_nums:
        comic_nums.append(comic_num)

    comic_nums.sort()
    # log.debug(f"Comic nums: {comic_nums}")

    with open(file, "w") as f:
        for num in comic_nums:
            f.write(f"{num}\n")


def get_saved_imgs(
    comic_img_dir: t.Union[str, Path] = COMIC_IMG_DIR, as_int: bool = True
) -> list[str] | list[int]:
    """Loop over comic images saved in `comic_img_dir` and extract comic number from filename.

    Params:
        comic_img_dir (str|Path): Path to a directory containing XKCD comic `.png`s.
        as_int (bool): Return list of integers if `True`.

    Returns:
        (list[str]): If `as_int = False`
        (list[int]): If `as_int = True`

    """
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


def validate_current_comic_file(current_comic_file: t.Union[str, Path] = None) -> Path:
    """Validate the current_comic.json file. Create template file, if current_comic.json does not exist.

    Params:
        current_comic_file (str|Path): Path to the `current_comic.json` file.

    """
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
) -> CurrentComicMeta:
    """Read the contents of the `current_comic.json` file.

    Params:
        current_comic_file (str|Path): Path to the `current_comic.json` file.

    """
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
        _metadata: CurrentComicMeta = CurrentComicMeta.model_validate(obj=_data)

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
    current_comic: CurrentComicMeta = None,
) -> bool:
    """Update the `current_comic.json` file with new data.

    Params:
        current_comic_file (str|Path): Path to the `current_comic.json` file.
        current_comic (CurrentComicMeta): A `CurrentComicMeta` object containing comic metadata, like comic number and a bool
            indicating whether the comic's image has been downloaded.

    """
    current_comic_file = validate_current_comic_file(
        current_comic_file=current_comic_file
    )
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
                cls=request_client.encoders.DateTimeEncoder,
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
