"""Modules for XKCD comics, meant to be imported & used in packages/pipelines."""

from __future__ import annotations

from . import response_handler
from .methods import (
    list_missing_nums,
    load_serialized_comic,
    make_comic_request,
    request_and_save_comic_img,
    save_comic_img,
    save_comic_img_to_db,
    save_comic_to_db,
    save_serialize_comic_object,
    update_current_comic_json,
    update_current_comic_meta_db,
)
