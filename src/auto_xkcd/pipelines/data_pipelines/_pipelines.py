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
from core.constants import PQ_ENGINE
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
    save_parquet: bool = True,
    pq_output_file: t.Union[str, Path] = COMICS_PQ_FILE,
    pq_engine: str = PQ_ENGINE,
):
    log.info(">> Start save serialized XKCD comics to database pipieline")

    log.info(
        f"Loading .msgpack file(s) in path  '{serialized_dir}' into Pandas DataFrame."
    )
    ## Load .msgpack serialized XKCDComic objects into a DataFrame
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

    log.info(f"Saving {comics_df.shape[0]} to database")
    ## Save DataFrame to SQLite database using SQLAlchemy engine
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

    if save_parquet:
        assert pq_output_file, ValueError(
            "save_parquet=True, but no pq_output_file detected."
        )

        log.info(
            f"Saving [{comics_df.shape[0]}] XKCD comic(s) to Parquet file '{pq_output_file}'"
        )
        ## Save DataFrame to .parquet file
        try:
            comics_df.to_parquet(pq_output_file, engine=pq_engine)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception saving XKCD comics DataFrame to Parquet file '{pq_output_file}'. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            log.warning(f"Did not save comics to Parquet file.")

    log.info(">> End save serialized XKCD comics to database pipieline")
