import typing as t
from pathlib import Path
from contextlib import AbstractContextManager

from core.paths import DATA_DIR, SERIALIZE_DIR, COMIC_IMG_DIR

from loguru import logger as log
from red_utils.std import path_utils


class SavedImgsController(AbstractContextManager):
    def __init__(self, img_dir: t.Union[str, Path] = COMIC_IMG_DIR):
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

    def __enter__(self):
        _imgs: list[Path] = []
        _img_nums: list[int] = []
        for p in path_utils.scan_dir(
            self.img_dir, as_pathlib=True, return_type="files"
        ):
            _imgs.append(p)
            _img_nums.append(int(p.stem))

        self.comic_imgs = sorted(_imgs)
        self.comic_nums = sorted(_img_nums)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            log.error(f"({exc_type}): {exc_value}")
            log.trace(traceback)

            return
