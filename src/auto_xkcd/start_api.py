from __future__ import annotations

from api.config import (
    APISettings,
    UvicornSettings,
    api_settings,
    uvicorn_settings,
)
from core.config import db_settings, settings
from domain.xkcd import comic
from loguru import logger as log
from packages import xkcd_comic
from setup import api_setup, setup_database
import uvicorn

def run_server(uvicorn_settings: UvicornSettings = None) -> None:
    """Run FastAPI app with Uvicorn."""
    try:
        uvicorn.run(
            app=uvicorn_settings.app,
            host=uvicorn_settings.host,
            port=uvicorn_settings.port,
            reload=uvicorn_settings.reload,
            root_path=uvicorn_settings.root_path,
        )
    except Exception as exc:
        msg = Exception(f"Unhandled exception running Uvicorn server. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc


if __name__ == "__main__":
    api_setup()
    setup_database(db_settings=db_settings)

    log.debug(f"API settings: {api_settings}")
    log.debug(f"Uvicorn settings: {uvicorn_settings}")

    ## Request current comic before starting API
    try:
        current_comic: comic.XKCDComic = xkcd_comic.current_comic.get_current_comic()
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting current comic before starting API. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

    log.info("Starting uvicorn server")
    log.debug(f"Uvicorn reload: {uvicorn_settings.reload}")
    try:
        run_server(uvicorn_settings=uvicorn_settings)
    except Exception as exc:
        msg = Exception(f"Unhandled exception running Uvicorn server. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc
