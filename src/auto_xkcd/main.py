from __future__ import annotations

import typing as t

from _setup import base_app_setup
from core import database, paths, request_client
from core.constants import PQ_ENGINE
from core.dependencies import db_settings, settings
from domain.pipelines import ExecutePipelineReport, PipelineHandler
from domain.xkcd.comic.schemas import XKCDComic
from entrypoints import pipeline_entrypoints
import hishel
import httpx
from loguru import logger as log
from modules import data_mod, xkcd_mod
from pipelines import execute_pipelines, pipeline_prefab

if __name__ == "__main__":
    base_app_setup()

    CACHE_TRANSPORT = request_client.get_cache_transport()

    log.info(
        "Main entrypoint, running sequence to get current comic, then scrape for missing comics, finally saving all comics to the database."
    )

    RUN_PIPELINES: list[PipelineHandler] = [
        pipeline_prefab.PIPELINE_CONF_CURRENT_COMIC,
        pipeline_prefab.PIPELINE_CONF_SAVE_SERIALIZED_TO_DB,
    ]

    ## Get the current comic, save existing serialized comics to database
    get_current_save_serialized_res: ExecutePipelineReport = execute_pipelines(
        pipelines_list=RUN_PIPELINES
    )
    log.info(
        f"Get current comic + saved serialized comics to database results: {get_current_save_serialized_res.results_str}"
    )

    scrape_missing_res: ExecutePipelineReport = execute_pipelines(
        pipelines_list=[pipeline_prefab.PIPELINE_CONF_SCRAPE_MISSING_COMICS]
    )
    log.info(f"Scrape missing comics results: {scrape_missing_res.results_str}")

    ## Re-run saving serialized comics to DB after other pipelines
    save_serialize_to_db: ExecutePipelineReport = execute_pipelines(
        pipelines_list=[pipeline_prefab.PIPELINE_CONF_SAVE_SERIALIZED_TO_DB]
    )
    log.info(
        f"Save serialized comics to database results: {save_serialize_to_db.results_str}"
    )
