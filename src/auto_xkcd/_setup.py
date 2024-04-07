from pathlib import Path

from core.config import AppSettings
from core.dependencies import settings
from core.paths import ENSURE_DIRS

from loguru import logger as log
from red_utils.ext.loguru_utils import init_logger, sinks
from red_utils.std import path_utils

DEFAULT_LOGGING_SINKS: list = [
    sinks.LoguruSinkStdErr(level=settings.log_level).as_dict(),
    sinks.LoguruSinkAppFile(sink=f"logs/{settings.env}/app.log").as_dict(),
    sinks.LoguruSinkErrFile(sink=f"logs/{settings.env}/err.log").as_dict(),
    sinks.LoguruSinkTraceFile(sink=f"logs/{settings.env}/trace.log").as_dict(),
]


def logging_setup(
    settings: AppSettings = settings, sinks: list = DEFAULT_LOGGING_SINKS
):
    assert settings, ValueError("Missing AppSettings object")
    assert isinstance(settings, AppSettings), TypeError(
        f"settings must be of type AppSettings. Got type: ({type(settings)})"
    )

    init_logger(sinks=DEFAULT_LOGGING_SINKS)
    log.info("Logging initialized")


def setup_ensure_dirs(ensure_dirs: list[Path] = ENSURE_DIRS):
    try:
        path_utils.ensure_dirs_exist(ensure_dirs=ensure_dirs)
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception ensuring directories exist. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc


def base_app_setup(
    settings: AppSettings = settings, ensure_dirs: list[Path] = ENSURE_DIRS
) -> None:
    assert settings, ValueError("Missing AppSettings object")
    assert isinstance(settings, AppSettings), TypeError(
        f"settings must be of type AppSettings. Got type: ({type(settings)})"
    )

    assert ensure_dirs, ValueError("Missing list of directories to ensure existence")
    assert isinstance(ensure_dirs, list), TypeError(
        f"ensure_dirs must be a list of Path objects"
    )

    logging_setup(settings=settings)
    setup_ensure_dirs(ensure_dirs=ensure_dirs)
