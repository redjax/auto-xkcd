from __future__ import annotations

from contextlib import AbstractContextManager
import json
from pathlib import Path
import typing as t

from core.constants import IGNORE_COMIC_NUMS
from core.paths import COMIC_IMG_DIR, CURRENT_COMIC_FILE, DATA_DIR, SERIALIZE_DIR
from loguru import logger as log
import pendulum
from red_utils.std import path_utils


def get_ts(
    as_str: bool = False, ts_format: str = "YYYY-MM-DD_HH:mm:ss"
) -> t.Union[str, pendulum.DateTime]:
    """Return a `pendulum.DateTime` or timestamp string.

    Params:
        as_str (bool): [Default: False] If `True`, return timestamp as a string.
        ts_format (str): Format the timestamp.

    """
    ts: pendulum.DateTime = pendulum.now()

    if as_str:
        ts: str = ts.format(ts_format)

    return ts


class SavedImgsController(AbstractContextManager):
    """Context manager to load all filenames (i.e. comic numbers) from images in the `img_dir` directory.

    Params:
        img_dir (str|Path): Path to the directory containing comic images.

    """

    def __init__(self, img_dir: t.Union[str, Path] = COMIC_IMG_DIR):  # noqa: D107
        assert img_dir, ValueError("Missing an img_dir")
        assert isinstance(img_dir, str) or isinstance(img_dir, Path), TypeError(
            f"img_dir must be of type str or Path. Got type: ({type(img_dir)})"
        )
        if isinstance(img_dir, str):
            img_dir: Path = Path(img_dir)
        if "~" in f"{img_dir}":
            img_dir: Path = Path(img_dir).expanduser()

        assert img_dir.exists(), FileNotFoundError(f"Could not find img_dir: {img_dir}")

        self.img_dir = img_dir
        self.comic_nums: list[int] = None
        self.comic_imgs: list[Path] = None

    def __enter__(self):  # noqa: D105
        _imgs: list[Path] = []
        _img_nums: list[int] = []

        try:
            for p in path_utils.scan_dir(
                self.img_dir, as_pathlib=True, return_type="files"
            ):
                log.debug(f"IGNORE_COMIC_NUMS ({type(IGNORE_COMIC_NUMS)})")
                log.debug(f"Path stem ({type(p.stem)}): {p.stem}")
                if int(p.stem) in IGNORE_COMIC_NUMS:
                    log.warning(f"Ignoring comic #{p.stem}")
                    continue

                _imgs.append(p)
                _img_nums.append(int(p.stem))

            self.comic_imgs = sorted(_imgs)
            self.comic_nums = sorted(_img_nums)

            return self

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception scanning path '{self.img_dir}' for saved comics. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            raise exc

    def __exit__(self, exc_type, exc_value, traceback):  # noqa: D105
        if exc_type:
            log.error(f"({exc_type}): {exc_value}")
            log.trace(traceback)

            return


class CurrentComicController(AbstractContextManager):
    """Handler for the current_comic.json file.

    Params:
        current_comic_file (str|Path): Path to the `current_comic.json` file.
        mode (str): [Default: "r"] The file mode for opening the `current_comic.json` file.

    """

    def __init__(  # noqa: D107
        self,
        current_comic_file: t.Union[str, Path] = CURRENT_COMIC_FILE,
        mode: str = "r",
    ):
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

        self.mode = mode.lower()
        self.current_comic_file: Path = current_comic_file
        self.current_comic_meta: dict = {
            "comic_num": None,
            "last_updated": None,
        }

    def __enter__(self):  # noqa: D105
        self.file = open(self.current_comic_file, self.mode)

        return self

    def __exit__(self, exc_type, exc_value, traceback):  # noqa: D105
        if exc_type:
            log.error(f"({exc_type}): {exc_value}")
            log.trace(traceback)

            return

        if self.file:
            self.file.close()

    def read(self) -> dict:
        """Read the file contents and load into a dict."""
        if self.mode != "r":
            raise ValueError(
                f"File not opened in read mode. Opened with mode: {self.mode}"
            )

        data: dict = json.load(self.file)

        return data

    def write(self, data) -> None:
        """Write data dict to JSON file."""
        if self.mode != "w":
            raise ValueError(
                f"File not opened in write mode. Opened with mode: {self.mode}"
            )

        json.dump(data, self.file)
