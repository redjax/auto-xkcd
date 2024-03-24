from __future__ import annotations

from .constants import CURRENT_XKCD_URL, XKCD_URL_BASE, XKCD_URL_POSTFIX
from .domain import (
    ComicNumCSVData,
    XKCDComic,
    XKCDComicModel,
    XKCDComicOut,
    XKCDComicRepository,
    XKCDSentComic,
    XKCDSentComicModel,
    XKCDSentComicOut,
    XKCDSentComicRepository,
)
from .requests_prefab import make_req, current_comic_req, comic_num_req
