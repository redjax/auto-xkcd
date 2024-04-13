"""Define global constants for modules/packages to use.

Includes values like `IGNORE_COMIC_NUMS`, which is a list of integers representing
comic numbers to ignore. This is useful to ignore joke comics like [comic #404](https://www.xkcd.com/404), which
returns an HTTP 404 response as a joke.
"""

from __future__ import annotations

IGNORE_COMIC_NUMS: list[int] = [404]

XKCD_URL_BASE: str = "https://xkcd.com"
XKCD_URL_POSTFIX: str = "info.0.json"
CURRENT_XKCD_URL: str = f"{XKCD_URL_BASE}/{XKCD_URL_POSTFIX}"

PQ_ENGINE: str = "fastparquet"
