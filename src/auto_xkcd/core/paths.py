from __future__ import annotations

from pathlib import Path

DATA_DIR: Path = Path(".data")
CACHE_DIR: Path = Path(f"{DATA_DIR}/cache")
SERIALIZE_DIR: Path = Path(f"{DATA_DIR}/serialize")
PQ_DIR: Path = Path(f"{DATA_DIR}/parquet")
BACKUP_DIR: Path = Path(f"{DATA_DIR}/backup")
COMIC_IMG_DIR: Path = Path(f"{DATA_DIR}/comic_imgs")

ENSURE_DIRS: list[Path] = [
    DATA_DIR,
    SERIALIZE_DIR,
    PQ_DIR,
    BACKUP_DIR,
    CACHE_DIR,
    COMIC_IMG_DIR,
]
