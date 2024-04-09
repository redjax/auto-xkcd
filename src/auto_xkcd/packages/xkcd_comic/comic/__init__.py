"""Request a specific comic, or multiple comics, or all missing comics."""

from __future__ import annotations

from .methods import get_multiple_comics, get_single_comic
from .scraper import scrape_missing_comics
