"""Pipelines string packages & modules together into chains of repeatable actions.

Pipelines can retrieve, process, and return results in a repeatable/factory-like way.
"""

from __future__ import annotations

from .schemas import (
    ExecutePipelineReport,
    PipelineConfig,
    PipelineHandler,
    PipelineLoopConfig,
)
