"""Utilities & methods for interacting with Python's `datetime` library.

This is meant to ease some common uses I have for `datetime`, like generating a timestamp with my preferred format,
or converting between `str` and `datetime.datetime`.
"""

from __future__ import annotations

from .constants import TIME_FMT_12H, TIME_FMT_24H
from .methods import datetime_as_dt, datetime_as_str, get_ts