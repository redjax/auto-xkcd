from pathlib import Path
import typing as t

from core.paths import (
    COMIC_IMG_DIR,
    SERIALIZE_COMIC_OBJECTS_DIR,
    SERIALIZE_COMIC_RESPONSES_DIR,
    COMICS_PQ_FILE,
    CURRENT_COMIC_FILE,
)
from core.dependencies import settings, db_settings
from core.config import AppSettings, DBSettings
from domain.xkcd.comic import XKCDComic
from helpers.validators import (
    validate_comic_nums_lst,
    validate_hishel_cachetransport,
    validate_path,
)
import hishel
import httpx
from loguru import logger as log
from modules import requests_prefab, xkcd_mod, data_mod
import msgpack
from packages import xkcd_comic
from utils import serialize_utils
import pandas as pd


def pipeline_ingest_data_bronze():
    """Open raw inputs (.msgpack, .txt, .csv, .json, etc) and load into database and/or Parquet file."""
    raise NotImplementedError(f"Data ingestion bronze pipeline not implemented.")


def pipeline_process_data_bronze():
    """Process the data, converting dtypes, changing column names, sorting objects, etc."""
    raise NotImplementedError(f"Data processing bronze pipeline n ot implmented.")


def pipeline_save_serialized_comics_to_db(
    serialized_dir: t.Union[str, Path] = SERIALIZE_COMIC_OBJECTS_DIR,
    tbl_name: str = "xkcd_comic",
    if_exists: str = "replace",
    index: bool = False,
    db_settings: DBSettings = db_settings,
):
    log.info(">> Start save serialized XKCD comics to database pipieline")

    try:
        comics_df: pd.DataFrame = data_mod.deserialize_comics_to_df(
            scan_path=serialized_dir
        )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception deserializing XKCDComic objects. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    try:
        comics_df.to_sql(
            name=tbl_name,
            con=db_settings.get_engine(),
            if_exists=if_exists,
            index=index,
        )

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception dumping DataFrame to SQLite. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    log.info(">> End save serialized XKCD comics to database pipieline")
