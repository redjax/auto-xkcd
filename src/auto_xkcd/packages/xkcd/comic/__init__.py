from .methods import (
    get_current_comic,
    get_multiple_comics,
    convert_dict_to_xkcdcomic,
    convert_response_to_dict,
    request_comic,
)
from . import scraper
from . import img
from .current import read_current_comic_meta, update_current_comic_meta
