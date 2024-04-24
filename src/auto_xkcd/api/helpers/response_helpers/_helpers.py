from __future__ import annotations

from pathlib import Path
import typing as t

from helpers import validators
from loguru import logger as log

def stream_file_contents(f_path: t.Union[str, Path] = None, mode: str = "rb"):
    if f_path is None:
        log.warning(ValueError("Missing a file path"))
        return None

    try:
        f_path = validators.validate_path(p=f_path, must_exist=True)
    except FileNotFoundError as fnf:
        msg = Exception(f"Could not find  file: '{f_path}'.")
        log.error(msg)

        raise fnf

    with open(f_path, mode=mode) as f_out:
        yield from f_out
