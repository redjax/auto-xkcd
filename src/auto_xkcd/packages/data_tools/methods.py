import typing as t
from pathlib import Path

from core import (
    SERIALIZE_COMIC_OBJECTS_DIR,
    SERIALIZE_COMIC_RESPONSES_DIR,
    SERIALIZE_DIR,
    DATA_DIR,
    PQ_DIR,
    COMICS_PQ_FILE,
    COMIC_IMG_DIR,
    CURRENT_COMIC_FILE,
    CURRENT_XKCD_URL,
    IGNORE_COMIC_NUMS,
)
from modules import data_mod

from loguru import logger as log
import pandas as pd
