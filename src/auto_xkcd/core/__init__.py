"""The `core` module stores globally accessible objects.

Configuration classes are defined here, as well as base database setup & some default variables for things like
directory paths & file paths.

Code in this module should not import from outside the `core` directory, if possible.
"""

from __future__ import annotations

from .constants import (
    CURRENT_XKCD_URL,
    IGNORE_COMIC_NUMS,
    XKCD_URL_BASE,
    XKCD_URL_POSTFIX,
)
from .dependencies import (
    db_settings,
    get_db,
    minio_settings,
    settings,
    telegram_settings,
)
from .paths import (
    BACKUP_DIR,
    CACHE_DIR,
    COMIC_IMG_DIR,
    DATA_DIR,
    ENSURE_DIRS,
    PQ_DIR,
    SERIALIZE_COMIC_OBJECTS_DIR,
    SERIALIZE_COMIC_RESPONSES_DIR,
    SERIALIZE_DIR,
)
