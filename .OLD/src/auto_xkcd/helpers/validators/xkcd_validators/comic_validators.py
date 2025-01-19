from __future__ import annotations

import typing as t

from core.constants import IGNORE_COMIC_NUMS

def validate_comic_nums_lst(comic_nums: list[int] = None) -> list[int]:
    """Return a validated list of integers.

    Params:
        comic_nums (list[int]): A list of `int` values representing XKCD comic numbers.

    Returns:
        (list[int]): A validated list of integers.

    """
    assert comic_nums, ValueError("comic_nums must be a list of integers.")
    assert isinstance(comic_nums, list), TypeError(
        f"comic_nums must be a list. Got type: ({type(comic_nums)})"
    )
    for i in comic_nums:
        assert isinstance(i, int), TypeError(
            f"All comic numbers in comic_nums list must be integers. Found type: ({type(i)})"
        )

    return comic_nums


def validate_comic_num(comic_num: int = None) -> int:
    assert comic_num, ValueError("Missing comic_num to validate")
    assert isinstance(comic_num, int), TypeError(
        f"comic_num must be an integer. Got type: ({type(comic_num)})"
    )
