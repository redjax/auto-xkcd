from __future__ import annotations

from api.config import APISettings, UvicornSettings, api_settings, uvicorn_settings
from core.config import db_settings, settings
from domain.xkcd import comic
from loguru import logger as log
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

    try:
        run_server(uvicorn_settings=uvicorn_settings)
    except Exception as exc:
        msg = Exception(f"Unhandled exception running Uvicorn server. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc
