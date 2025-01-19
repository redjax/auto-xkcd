from __future__ import annotations

from dynaconf import Dynaconf
from loguru import logger as log

LOGGING_SETTINGS = Dynaconf(
    environments=True,
    envvar_prefix="LOG",
    settings_files=["settings.toml", ".secrets.toml"]
)
