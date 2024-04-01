from __future__ import annotations

from .context_managers import ComicNumsController

def get_comic_nums() -> list[int]:
    """Return list of comic numbers from controller."""
    with ComicNumsController() as comic_nums_ctl:
        comic_nums: list[int] = comic_nums_ctl.as_list()

        return comic_nums
