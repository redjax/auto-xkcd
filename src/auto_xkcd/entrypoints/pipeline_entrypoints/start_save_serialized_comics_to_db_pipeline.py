"""Pipeline for saving retrieved comics to the database.

Loops over serialized XKCDComic `.msgpack` files, deserializing them into a Pandas `DataFrame`
and saving the DataFrame using the app's SQLAlchemy connection.
"""

from __future__ import annotations

from pathlib import Path
import typing as t

from setup import base_app_setup
from core import database
from core.config import DBSettings
from core.constants import PQ_ENGINE
from core.dependencies import db_settings
from core.paths import COMICS_PQ_FILE, SERIALIZE_COMIC_OBJECTS_DIR
from loguru import logger as log
from pipelines import data_pipelines
import sqlalchemy as sa
import sqlalchemy.orm as so


def run_pipeline(
    db_settings: DBSettings = db_settings,
    sqla_base: so.DeclarativeBase = database.Base,
    serialized_comics_dir: t.Union[str, Path] = SERIALIZE_COMIC_OBJECTS_DIR,
    db_comics_tbl_name: str = "xkcd_comic",
    if_exists_strategy: str = "replace",
    include_df_index: bool = False,
    save_parquet: bool = True,
    pq_output_file: t.Union[str, Path] = COMICS_PQ_FILE,
    pq_engine: str = PQ_ENGINE,
):
    """Entrypoint to start the pipeline.

    Params:
        db_settings (DBSettings): Initialized instance of `DBSettings` class.
        sqla_base (sqlalchemy.orm.DeclarativeBase): The `SQLAlchemy` `DeclarativeBase` object for the app's table classes.
        serialized_comics_dir (str|Path): Path to directory where `.msgpack`-serialized XKCDComics are saved.
        db_comics_tbl_name (str): Database table name for comics saved using this pipeline.
        if_exists_strategy (str): The Pandas strategy for handling entities that already exist in the database. `Default: 'replace'`
        include_df_index (bool): When `True`, includes the Pandas `DataFrame` index as a column. `Default: False`
        save_parquet (bool): When `True`, saves the `DataFrame` as a `.parquet` file. `Default: True`
        pq_output_file (str|Path): Path to the `.parquet` file where `DataFrame` will be saved. Only used if `save_parquet=True`.
        pq_engine (str): The parquet package to use for saving, i.e. `pyarrow` or `fastparquet`. `Default: <defined in core.constants.PQ_ENGINE>`
    """
    db_engine: sa.Engine = db_settings.get_engine()

    try:
        database.create_base_metadata(base=sqla_base, engine=db_engine)
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception creating SQLAlchemy Base metadata. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        log.warning(
            f"Continuing without initializing database. This will probably cause issues."
        )

    try:
        data_pipelines.pipeline_save_serialized_comics_to_db(
            serialized_dir=serialized_comics_dir,
            tbl_name=db_comics_tbl_name,
            if_exists=if_exists_strategy,
            index=include_df_index,
            db_settings=db_settings,
            save_parquet=save_parquet,
            pq_output_file=pq_output_file,
            pq_engine=PQ_ENGINE,
        )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception running pipeline to save serialized XKCDComic objects to database. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc


if __name__ == "__main__":
    base_app_setup()

    run_pipeline()
