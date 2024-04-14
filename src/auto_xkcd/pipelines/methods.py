from __future__ import annotations

from domain.pipelines import ExecutePipelineReport, PipelineHandler
from loguru import logger as log

def execute_pipelines(
    pipelines_list: list[PipelineHandler] = None,
) -> ExecutePipelineReport:
    """Iterate over a list of PipelineHandler objects & execute each one."""
    success: list[PipelineHandler] = []
    fail: list[PipelineHandler] = []

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
