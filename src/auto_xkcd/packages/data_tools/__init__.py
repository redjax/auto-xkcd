from __future__ import annotations

from pathlib import Path
import typing as t

from core import (
    COMIC_IMG_DIR,
    COMICS_PQ_FILE,
    CURRENT_COMIC_FILE,
    CURRENT_XKCD_URL,
    DATA_DIR,
    IGNORE_COMIC_NUMS,
    PQ_DIR,
    SERIALIZE_COMIC_OBJECTS_DIR,
    SERIALIZE_COMIC_RESPONSES_DIR,
    SERIALIZE_DIR,
)
from loguru import logger as log
from modules import data_mod
import pandas as pd
