import typing as t


def validate_comic_nums_lst(comic_nums: list[int] = None) -> list[int]:
    """Return a validated list of integers."""
    assert comic_nums, ValueError("comic_nums must be a list of integers.")
    assert isinstance(comic_nums, list), TypeError(
        f"comic_nums must be a list. Got type: ({type(comic_nums)})"
    )
    for i in comic_nums:
        assert isinstance(i, int), TypeError(
            f"All comic numbers in comic_nums list must be integers. Found type: ({type(i)})"
        )

    return comic_nums
