from .paths import (
    ENSURE_DIRS,
    DATA_DIR,
    CACHE_DIR,
    SERIALIZE_DIR,
    PQ_DIR,
    BACKUP_DIR,
    COMIC_IMG_DIR,
)
from .constants import (
    IGNORE_COMIC_NUMS,
    XKCD_URL_BASE,
    XKCD_URL_POSTFIX,
    CURRENT_XKCD_URL,
)
from .dependencies import db_settings, minio_settings, settings, telegram_settings
