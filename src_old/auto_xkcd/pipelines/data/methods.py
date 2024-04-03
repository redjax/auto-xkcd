from __future__ import annotations

from pathlib import Path
import time
import typing as t

from core import COMIC_IMG_DIR
from loguru import logger as log
from packages import xkcd

def pipeline_update_img_saved_vals(imgs_dir: Path = COMIC_IMG_DIR) -> None:
    """Iterate over all requested comics & saved images, set `True` values for images downloaded."""
    log.info(">> Start update 'img_saved' CSV value pipeline")
    try:
        xkcd.helpers.update_comic_num_img_bool(img_dir=imgs_dir)
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception running pipeline to update 'img_saved' value in CSV file. Details: {exc}"
        )
        log.error(msg)

        raise msg

    log.info("<< End update 'img_saved' CSV value pipeline")
