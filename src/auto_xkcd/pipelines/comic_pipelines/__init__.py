"""Pipelines/workflows for XKCD comic operations."""

from __future__ import annotations

from ._pipelines import (
    pipeline_current_comic,
    pipeline_multiple_comics,
    pipeline_scrape_missing_comics,
)
