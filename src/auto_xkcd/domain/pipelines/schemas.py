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
    pass


class PipelineConfigBase(BaseModel):
    name: str = Field(
        default="unnamed_pipeline",
        description="Optionally, give pipeline configuration a name, i.e. 'current_comic_pipeline'",
    )
    loop_settings: PipelineLoopConfig | None = Field(default=None)


class PipelineConfig(PipelineConfigBase):
    pass
