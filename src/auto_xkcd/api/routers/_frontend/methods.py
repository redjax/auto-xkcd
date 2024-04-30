from __future__ import annotations

from pathlib import Path

from fastapi.templating import Jinja2Templates
from loguru import logger as log

def get_templates_dir(templates_dirname: str = "templates") -> Jinja2Templates:
    if not Path(f"{templates_dirname}").exists():
        raise FileNotFoundError("Directory not found: 'templates'")
    else:
        log.debug("Found templates dir.")
        return Jinja2Templates(directory=templates_dirname)
