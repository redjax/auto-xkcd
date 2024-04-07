from __future__ import annotations

from . import img, scraper
from .current import read_current_comic_meta, update_current_comic_meta
from .methods import (
    convert_dict_to_xkcdcomic,
    convert_response_to_dict,
    get_current_comic,
    get_multiple_comics,
    get_specific_comic,
    request_comic,
)
