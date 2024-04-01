from __future__ import annotations

from pathlib import Path
import typing as t

from .context_managers import ComicNumsController

from core.paths import COMIC_IMG_DIR
from loguru import logger as log
import pandas as pd
from red_utils.std import path_utils

def get_comic_nums() -> list[int]:
    """Return list of comic numbers from controller."""
    with ComicNumsController() as comic_nums_ctl:
        comic_nums: list[int] = comic_nums_ctl.as_list()

        return comic_nums


def update_comic_num_img_bool(img_dir: t.Union[str, Path] = COMIC_IMG_DIR) -> None:
    """Iterate over saved comic data, updating img_saved value based on downloaded imgs."""
    assert img_dir, ValueError("Missing path to directory with comic images.")
    assert isinstance(img_dir, str) or isinstance(img_dir, Path), TypeError(
        f"img_dir must be a string or Path. Got type: ({type(img_dir)})"
    )
    if isinstance(img_dir, str):
        if "~" in img_dir:
            img_dir: Path = Path(img_dir).expanduser()
        else:
            img_dir: Path = Path(img_dir)
    if isinstance(img_dir, Path):
        if "~" in f"{img_dir}":
            img_dir = img_dir.expanduser()

    img_files: list[Path] = path_utils.scan_dir(
        target=img_dir, as_pathlib=True, return_type="files"
    )

    log.info(
        f"Updating comic_nums CSV file 'img_saved' values, based on files found in path '{img_dir}'."
    )

    try:
        with ComicNumsController() as comic_num_ctl:
            for img_f in img_files:
                img_name: str = img_f.stem
                # log.debug(f"img_name: {img_name}")

                try:
                    matching_rows: pd.DataFrame = comic_num_ctl.df[
                        comic_num_ctl.df["comic_num"] == int(img_name)
                    ]
                except Exception as exc:
                    msg = Exception(
                        f"Unhandled exception matching row in DataFrame to comic num '{img_name}'. Details: {exc}"
                    )
                    log.error(msg)

                    raise msg

                for index, row in matching_rows.iterrows():
                    ## Check if img_saved = False
                    if not row["img_saved"]:
                        ## Update value if False
                        comic_num_ctl.df.at[index, "img_saved"] = True
                        log.debug(
                            f"Updated img_saved value for comic_num {img_name}. Set to True."
                        )

            log.success(f"Finished updating CSV file 'img_saved' values.")
            log.debug(f"DataFrame preview:\n{comic_num_ctl.df.head(5)}")

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting ComicNumsController context manager. Details: {exc}"
        )
        log.error(msg)

        raise msg
