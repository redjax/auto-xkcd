from __future__ import annotations

from pathlib import Path

DATA_DIR: Path = Path(".data")
CACHE_DIR: Path = Path(f"{DATA_DIR}/cache")
SERIALIZE_DIR: Path = Path(f"{DATA_DIR}/serialize")
PQ_DIR: Path = Path(f"{DATA_DIR}/parquet")
BACKUP_DIR: Path = Path(f"{DATA_DIR}/backup")
COMIC_IMG_DIR: Path = Path(f"{DATA_DIR}/comic_imgs")

SERIALIZE_COMIC_RESPONSES_DIR: Path = Path(f"{SERIALIZE_DIR}/comic_responses")
SERIALIZE_COMIC_OBJECTS_DIR: Path = Path(f"{SERIALIZE_DIR}/xkcdcomic_objects")

ENSURE_DIRS: list[Path] = [
    DATA_DIR,
    SERIALIZE_DIR,
    SERIALIZE_COMIC_RESPONSES_DIR,
    SERIALIZE_COMIC_OBJECTS_DIR,
    PQ_DIR,
    BACKUP_DIR,
    CACHE_DIR,
    COMIC_IMG_DIR,
]

CURRENT_COMIC_FILE: Path = Path(f"{DATA_DIR}/current_comic.json")
