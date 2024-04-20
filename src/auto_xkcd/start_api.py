from core.config import db_settings, settings
from api._config import APISettings, UvicornSettings, api_settings, uvicorn_settings
from _setup import api_setup
from loguru import logger as log
from pydantic import BaseModel
from red_utils.ext.fastapi_utils import uvicorn_override
from red_utils.ext.loguru_utils import init_logger, sinks
import uvicorn


def run_server(uvicorn_settings: UvicornSettings = None) -> None:

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

    log.debug(f"API settings: {api_settings}")
    log.debug(f"Uvicorn settings: {uvicorn_settings}")

    run_server(uvicorn_settings=uvicorn_settings)
