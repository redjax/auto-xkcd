import typing as t
from pathlib import Path

from core.paths import DATA_DIR

from loguru import logger as log


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
