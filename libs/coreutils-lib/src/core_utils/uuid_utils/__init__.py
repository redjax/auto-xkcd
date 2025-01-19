"""Utilities for generating/splicing a UUID string using Python's `uuid.UUID` module.
"""

from __future__ import annotations

from .classes import UUIDLength
from .constants import glob_uuid_lens
from .operations import first_n_chars, gen_uuid, get_rand_uuid, trim_uuid