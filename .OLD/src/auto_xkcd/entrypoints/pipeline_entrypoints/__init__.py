"""Entrypoints for app pipelines, i.e. requesting the current comic."""

from __future__ import annotations

from . import (
    start_current_comic_pipeline,
    start_multiple_comic_pipeline,
    start_save_serialized_comics_to_db_pipeline,
    start_scrape_missing_pipeline,
)
