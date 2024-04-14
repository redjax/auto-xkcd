"""Pre-made `PipelineConfig` class instances, which can be imported & passed to methods that make use of a `PipelineConfig`."""

from pipelines.pipeline_config._config import PipelineConfig
from core.dependencies import CACHE_TRANSPORT, db_settings
from core import paths, database, PQ_ENGINE

from entrypoints.pipeline_entrypoints import (
    start_current_comic_pipeline,
    start_multiple_comic_pipeline,
    start_save_serialized_comics_to_db_pipeline,
    start_scrape_missing_pipeline,
)
from loguru import logger as log

## Current comic pipeline
PIPELINE_CONF_CURRENT_COMIC: PipelineConfig = PipelineConfig(
    name="get_current_comic",
    descripton="Run through operations to get, serialize, convert, & return the current XKCDComic.",
    method=start_current_comic_pipeline.run_pipeline,
    kwargs={"cache_transport": CACHE_TRANSPORT},
)

## Load serialized, save to db pipeline
PIPELINE_CONF_SAVE_SERIALIZED_TO_DB: PipelineConfig = PipelineConfig(
    name="save_serialized_comics_to_db",
    description="Iterate over serialized comic .msgpack files, load into a DataFrame, & save to the xkcd_comic DB table.",
    method=start_save_serialized_comics_to_db_pipeline.run_pipeline,
    kwargs={
        "db_settings": db_settings,
        "sqla_base": database.Base,
        "db_comics_tbl_name": "xkcd_comic",
        "if_exists_strategy": "replace",
        "include_df_index": False,
        "save_parquet": True,
        "pq_output_file": paths.COMICS_PQ_FILE,
        "pq_engine": PQ_ENGINE,
    },
)

## Scrape missing comics pipeline
PIPELINE_CONF_SCRAPE_MISSING_COMICS: PipelineConfig = PipelineConfig(
    name="scrape_missing_comics",
    description="Iterate over comic numbers from 1 to the current number, requesting & saving each comic.",
    method=start_scrape_missing_pipeline.run_pipeline,
    kwargs={
        "cache_transport": CACHE_TRANSPORT,
        "request_sleep": 5,
        "overwrite_serialized_comic": True,
        "max_list_size": 50,
        "loop_limit": None,
        "loop_pause": 10,
    },
)
