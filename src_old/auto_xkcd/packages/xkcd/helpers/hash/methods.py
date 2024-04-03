from __future__ import annotations

import httpx
from red_utils.std import hash_utils

def url_hash(url: str | httpx.URL = None) -> str:
    assert url, ValueError("Missing a URL to hash")
    assert isinstance(url, str) or isinstance(url, httpx.URL), TypeError(
        f"url must be of type str or httpx.URL. Got type: ({type(url)})"
    )

    try:
        if isinstance(url, str):
            _hash: str = hash_utils.get_hash_from_str(input_str=url)
        else:
            _hash: str = hash_utils.get_hash_from_str(input_str=str(url))

        return _hash
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception hashing URL to string. URL: {url}. Details: {exc}"
        )

        raise msg


def comic_num_hash(comic_num: int | str = None) -> str:
    assert comic_num, ValueError("Missing comic number to hash")
    assert isinstance(comic_num, int) or isinstance(comic_num, str), TypeError(
        f"comic_num must be an integer or string. Got type: ({type(comic_num)})"
    )
    if isinstance(comic_num, int):
        comic_num: str = f"{comic_num}"

    try:
        _hash: str = hash_utils.get_hash_from_str(input_str=comic_num)

        return _hash
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting hash from comic num string '{comic_num}'. Details: {exc}"
        )

        raise msg
