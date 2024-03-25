from __future__ import annotations

from .config import (
    AppSettings,
    DBSettings,
    TelegramSettings,
    db_settings,
    settings,
    telegram_settings,
)
from .dependencies import get_db
from .paths import (
    BACKUP_DIR,
    CACHE_DIR,
    DATA_DIR,
    ENSURE_DIRS,
    PQ_DIR,
    SERIALIZE_DIR,
    COMIC_IMG_DIR,
)
