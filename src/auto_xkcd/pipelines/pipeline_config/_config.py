import typing as t
from pydantic import (
    BaseModel,
    field_validator,
    Field,
    ValidationError,
    ConfigDict,
    computed_field,
)

from loguru import logger as log


class PipelineConfig(BaseModel):
    """Class controller for a pipeline module.

    Import a pipeline from `pipelines.*_pipelines`, and set `PipelineConfig.method` to the pipeline's `run_pipeline()` method. Each
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
