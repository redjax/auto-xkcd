"""The `core` module stores globally accessible objects.

Configuration classes are defined here, as well as base database setup & some default variables for things like
directory paths & file paths.

Code in this module should not import from outside the `core` directory, if possible.
"""

from __future__ import annotations

from .constants import (
    CURRENT_XKCD_URL,
    IGNORE_COMIC_NUMS,
    PQ_ENGINE,
    XKCD_URL_BASE,
    XKCD_URL_POSTFIX,
)
from .dependencies import (
    get_db,
)
from .config import (
    db_settings,
    # minio_settings,
    settings,
    telegram_settings,
)
from .config import AppSettings, DBSettings, MinioSettings, TelegramSettings
from .paths import (
    BACKUP_DIR,
    CACHE_DIR,
    COMIC_IMG_DIR,
    COMICS_PQ_FILE,
    CURRENT_COMIC_FILE,
    DATA_DIR,
    ENSURE_DIRS,
    PQ_DIR,
    SERIALIZE_COMIC_OBJECTS_DIR,
    SERIALIZE_COMIC_RESPONSES_DIR,
    SERIALIZE_DIR,
)
