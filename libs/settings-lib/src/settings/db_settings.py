from __future__ import annotations

from dynaconf import Dynaconf
from loguru import logger as log

## Database settings loaded with dynaconf
DB_SETTINGS: Dynaconf = Dynaconf(
    environments=True,
    envvar_prefix="DB",
    settings_files=["database/settings.toml", "database/.secrets.toml"],
)
