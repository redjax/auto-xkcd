from __future__ import annotations

from .context_managers.file import CurrentComicController, SavedImgsController
from .methods import get_saved_imgs, update_comic_nums_file
from .methods import (
    read_current_comic_meta,
    update_current_comic_meta,
    validate_current_comic_file,
)
