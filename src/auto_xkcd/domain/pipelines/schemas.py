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
