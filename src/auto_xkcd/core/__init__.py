"""The `core` module stores globally accessible objects.

Configuration classes are defined here, as well as base database setup & some default variables for things like
directory paths & file paths.

Code in this module should not import from outside the `core` directory, if possible.
"""

from __future__ import annotations

from .config import (
    AppSettings,
    DBSettings,
    MinioSettings,
    TelegramSettings,
    db_settings,
    # minio_settings,
    settings,
    telegram_settings,
)
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
    SERIALIZE_TELEGRAM_DIR,
    TELEGRAM_CHAT_ID_FILE,
    CELERY_DATA_DIR,
    CELERY_SQLITE_BACKEND_URI,
    CELERY_SQLITE_BROKER_URI,
    CELERY_SQLITE_RESULT_URI,
)
