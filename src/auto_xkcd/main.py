from domain.xkcd.comic.schemas import XKCDComic
from entrypoints import pipeline_entrypoints
from _setup import base_app_setup
from core.dependencies import settings, db_settings
from core import request_client, database, paths
from core.constants import PQ_ENGINE
from modules import xkcd_mod, data_mod


from loguru import logger as log
import hishel
import httpx


def execute_pipelines(pipelines_list: list[dict] = None):
    for _pipeline in pipelines_list:
        log.debug(f"Pipeline: {_pipeline}")
        log.info(f"Running '{_pipeline['name']}")

        try:
            _pipeline["method"](**_pipeline["args"])
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception running '{_pipeline['name']}'. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)


if __name__ == "__main__":
    base_app_setup()

    CACHE_TRANSPORT = request_client.get_cache_transport()

    PIPELINE_CONF_CURRENT_COMIC = {
        "name": "get_current_comic",
        "method": pipeline_entrypoints.start_current_comic_pipeline.run_pipeline,
        "args": {"cache_transport": CACHE_TRANSPORT},
    }
    PIPELINE_CONF_SAVE_SERIALIZED_TO_DB = {
        "name": "save_serialized_comics_to_db",
        "method": pipeline_entrypoints.start_save_serialized_comics_to_db_pipeline.run_pipeline,
        "args": {
            "db_settings": db_settings,
            "sqla_base": database.Base,
            "db_comics_tbl_name": "xkcd_comic",
            "if_exists_strategy": "replace",
            "include_df_index": False,
            "save_parquet": True,
            "pq_output_file": paths.COMICS_PQ_FILE,
            "pq_engine": PQ_ENGINE,
        },
    }
    PIPELINE_CONF_SCRAPE_MISSING_COMICS = {
        "name": "scrape_missing_comics",
        "method": pipeline_entrypoints.start_scrape_missing_pipeline.run_pipeline,
        "args": {
            "cache_transport": CACHE_TRANSPORT,
            "request_sleep": 5,
            "overwrite_serialized_comic": True,
            "max_list_size": 50,
            "loop_limit": None,
            "loop_pause": 10,
        },
    }

    RUN_PIPELINES: list[dict] = [
        PIPELINE_CONF_CURRENT_COMIC,
        PIPELINE_CONF_SAVE_SERIALIZED_TO_DB,
    ]

    execute_pipelines(pipelines_list=RUN_PIPELINES)

    execute_pipelines(pipelines_list=[PIPELINE_CONF_SCRAPE_MISSING_COMICS])
    execute_pipelines(pipelines_list=[PIPELINE_CONF_SAVE_SERIALIZED_TO_DB])
