from __future__ import annotations

from pathlib import Path
import typing as t

from loguru import logger as log
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    computed_field,
    field_validator,
)

class PipelineLoopConfigBase(BaseModel):
    loop: bool = Field(default=False, description="Apply loop configuration if True")
    loop_pause: t.Union[int, float] = Field(
        default=0, description="Time (in seconds) to wait/pause between loops"
    )
    max_loops: int | None = Field(default=None, description="Maximum number of loops")
    continue_on_error: bool = Field(
        default=False,
        description="If True, pipeline loop will continue when an error occurs, instead of exiting",
    )


class PipelineLoopConfig(PipelineLoopConfigBase):
    """Configuration for a pipeline's looping functionality.

    THIS CLASS IS NOT READY FOR USE.

    Params:
        loop (bool): [Default: `False`] If `True`, apply loop configurations to the pipeline.
        loop_pause (int|float): Time (in seconds) to wait/pause between loops.
        max_loops (int|None): [Default: None] If set, pipeline will loop numer of times defined.
        continue_on_error (bool): If `True`, pipeline loop will continue passed errored loops instead of exiting.
    """

    pass


class PipelineConfigBase(BaseModel):
    name: str = Field(
        default="unnamed_pipeline",
        description="Optionally, give pipeline configuration a name, i.e. 'current_comic_pipeline'",
    )
    loop_settings: PipelineLoopConfig | None = Field(default=None)


class PipelineConfig(PipelineConfigBase):
    """Store configuration for a pipeline.

    Params:
        name (str): Name for the pipeline
        loop_settings (PipelineeLoopConfig): Configurations for looping, if pipeline supports loops.

    """

    pass


class PipelineHandler(BaseModel):
    """Class controller for a pipeline module.

    Import a pipeline from `pipelines.*_pipelines`, and set `PipelineHandler.method` to the pipeline's `run_pipeline()` method. Each
    pipeline for this application has a `run_pipeline()` entrypoint, where params like an http cache transport or database connection object
    can be passed through to the calls the pipeline makes.

    This makes for repeatable, debuggable pipeline calls, and contains each pipelines' configuration to a single object, making them more portable.

    Params:
        name (str): A name for the pipeline. Use Python naming, i.e. 'pipeline_rename_files'.
        description(str|None): A short message describing the purpose of the pipeline.
        method (Callable): A `Callable` object, like a method or context manager. This should be the pipeline's `run_pipeline()`.
        kwargs (dict[str, Any]): A `dict` with configurations for the class's `method`. For example, if the `method` requires a
            `hishel.CacheTransport` object as a param named `cache_transport`, you could use:
            ```
            pipeline_config.kwargs = {"cache_transport": hishel.CacheTransport()}
            ```

    """

    name: str = Field(default=None)
    description: str | None = Field(default=None)
    method: t.Callable = Field(default=None)
    kwargs: dict[str, t.Any] = Field(default_factory={})

    def start(self) -> bool:
        try:
            self.method(**self.kwargs)
            log.success(f"Pipeline '{self.name}' finished.")

            return True

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception running pipeline '{self.name}'. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            return False


class ExecutePipelineReport(BaseModel):
    pipeline_execution_count: int = Field(default=0)
    success: list[PipelineHandler] | None = Field(default_factory=[])
    fail: list[PipelineHandler] | None = Field(default_factory=[])

    @computed_field
    @property
    def results_str(self) -> str:
        return f"[Total Pipelines Executed: {self.pipeline_execution_count}] | [SUCCESS:{len(self.success)}] [FAIL:{len(self.fail)}]"
