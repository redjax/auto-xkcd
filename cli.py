from __future__ import annotations

from cyclopts import App
from loguru import logger as log
from settings.logging_settings import LOGGING_SETTINGS
import setup
from project_cli.main import app as cli_app

def start_cli(app: App):
    try:
        cli_app.meta()
    except Exception as exc:
        msg = f"({type(exc)}) error"
        log.error(msg)
        
        raise exc
    
if __name__ == "__main__":
    setup.setup_loguru_logging(log_level="ERROR", log_fmt="basic")
    start_cli(app=cli_app)
