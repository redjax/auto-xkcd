import typing as t

from domain.xkcd.comic.schemas import XKCDComic
from entrypoints import pipeline_entrypoints
from pipelines import PipelineConfig, pipeline_config
from _setup import base_app_setup
from core.dependencies import settings, db_settings
from core import request_client, database, paths
from core.constants import PQ_ENGINE
from modules import xkcd_mod, data_mod

from loguru import logger as log
import hishel
import httpx

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    ValidationError,
    ConfigDict,
    computed_field,
)

from pipelines import pipeline_prefab


class ExecutePipelineReport(BaseModel):
    pipeline_execution_count: int = Field(default=0)
    success: list[PipelineConfig] | None = Field(default_factory=[])
    fail: list[PipelineConfig] | None = Field(default_factory=[])

    @computed_field
    @property
    def results_str(self) -> str:
        return f"[Total Pipelines Executed: {self.pipeline_execution_count}] | [SUCCESS:{len(self.success)}] [FAIL:{len(self.fail)}]"


def execute_pipelines(
    pipelines_list: list[PipelineConfig] = None,
) -> ExecutePipelineReport:

    success: list[PipelineConfig] = []
    fail: list[PipelineConfig] = []

    pipeline_execute_count: int = 0

    for _pipeline in pipelines_list:
        log.debug(f"Pipeline: {_pipeline}")

        try:
            _pipeline.start()
            success.append(_pipeline)

            pipeline_execute_count += 1
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception executing pipeline '{_pipeline.name}'. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            fail.append(_pipeline)

            pipeline_execute_count += 1

            continue

    ## Create pipeline execution report
    REPORT: ExecutePipelineReport = ExecutePipelineReport(
        pipeline_execution_count=pipeline_execute_count, success=success, fail=fail
    )

    return REPORT


if __name__ == "__main__":
    base_app_setup()

    CACHE_TRANSPORT = request_client.get_cache_transport()

    log.info(
        "Main entrypoint, running sequence to get current comic, then scrape for missing comics, finally saving all comics to the database."
    )

    RUN_PIPELINES: list[PipelineConfig] = [
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
