from __future__ import annotations

from cyclopts import App
from loguru import logger as log
from weather_cli.main import app as cli_app

def start_cli():
    try:
        cli_app.meta()
    except Exception as exc:
        msg = f"({type(exc)}) error"
        log.error(msg)
        
        raise exc
    
if __name__ == "__main__":
    start_cli()
