import typing as t
from pathlib import Path

from core.paths import DATA_DIR, COMIC_IMG_DIR, SERIALIZE_DIR

from loguru import logger as log
from red_utils.std import path_utils


def update_comic_nums_file(
    file: t.Union[str, Path] = f"{DATA_DIR}/comic_nums.txt", comic_num: int = None
):
    assert comic_num, ValueError("Missing comic number")
    assert isinstance(comic_num, int), TypeError(f"comic_num must be an integer")

    assert isinstance(file, str) or isinstance(file, Path), TypeError(
        f"file must be a string or Path object. Got type: ({type(file)})"
    )
    if isinstance(file, str):
        file: Path = Path(file)
    if "~" in f"{file}":
        file: Path = file.expanduser()

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

    with open(file, "r") as f:
        lines = f.readlines()
        comic_nums: list[int] = []
        for line in lines:
            stripped = int(line.strip())
            comic_nums.append(stripped)

    if comic_num not in comic_nums:
        log.debug(f"Comic num [{comic_num}] not in comic_nums: {comic_nums}")
        lines.append(comic_num)
        with open(file, "w") as f:
            for line in lines:
                f.write(f"{line}\n")


def get_saved_imgs(
    comic_img_dir: t.Union[str, Path] = COMIC_IMG_DIR, as_int: bool = True
) -> list[str] | list[int]:
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
