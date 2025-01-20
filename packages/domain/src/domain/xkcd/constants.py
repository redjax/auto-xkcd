from __future__ import annotations

IGNORE_COMIC_NUMS: list[int] = [404]

XKCD_URL_BASE: str = "https://xkcd.com"
XKCD_URL_POSTFIX: str = "info.0.json"
CURRENT_XKCD_URL: str = f"{XKCD_URL_BASE}/{XKCD_URL_POSTFIX}"
