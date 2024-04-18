"""Data control methods/context managers.

Responsible for things like creating/updating a running list of comic numbers successfully requested.
"""

from __future__ import annotations

from .context_managers.file import CurrentComicController, SavedImgsController
from .context_managers.df import IbisDuckDBController, DuckDBController
from .methods import (
    get_saved_imgs,
    read_current_comic_meta,
    update_comic_nums_file,
    update_current_comic_meta,
    validate_current_comic_file,
)
