"""Methods meant to be called early during execution.

Handle setup tasks, like creating directories that must exist, initializing logging, etc.

"""

from __future__ import annotations

from pathlib import Path

from core.config import AppSettings
from core.dependencies import settings
from core.paths import ENSURE_DIRS
from loguru import logger as log
from red_utils.ext.loguru_utils import init_logger, sinks
from red_utils.std import path_utils

## Default loguru sinks
DEFAULT_LOGGING_SINKS: list = [
    sinks.LoguruSinkStdErr(level=settings.log_level).as_dict(),
    sinks.LoguruSinkAppFile(sink=f"logs/{settings.env}/app.log").as_dict(),
    sinks.LoguruSinkErrFile(sink=f"logs/{settings.env}/err.log").as_dict(),
    sinks.LoguruSinkTraceFile(sink=f"logs/{settings.env}/trace.log").as_dict(),
]


def setup_logging(
    settings: AppSettings = settings, sinks: list = DEFAULT_LOGGING_SINKS
) -> None:
    """Initialize app logging (with Loguru).

    Params:
        settings (AppSettings): An initialized instance of `AppSettings`.
        sinks (list): A list of `loguru` sink dicts for the global logger.
    """
    assert settings, ValueError("Missing AppSettings object")
    assert isinstance(settings, AppSettings), TypeError(
        f"settings must be of type AppSettings. Got type: ({type(settings)})"
    )

    init_logger(sinks=sinks)
    log.info("Logging initialized")


def setup_ensure_dirs(ensure_dirs: list[Path] = ENSURE_DIRS) -> None:
    """Loop over list of Paths, create them if they do not exist.

    Params:
        ensure_dirs (list[Path]): A list of `Path` values to loop over & create, if they do not exist.
    """
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
    """Run setup methods.

    Params:
        settings (AppSettings): An initialized instance of AppSettings.
        ensure_dirs (list[Path]): A list of `Path` values to loop over and create, if they do not exist.

    """
    assert settings, ValueError("Missing AppSettings object")
    assert isinstance(settings, AppSettings), TypeError(
        f"settings must be of type AppSettings. Got type: ({type(settings)})"
    )

    assert ensure_dirs, ValueError("Missing list of directories to ensure existence")
    assert isinstance(ensure_dirs, list), TypeError(
        f"ensure_dirs must be a list of Path objects"
    )

    setup_logging(settings=settings)
    setup_ensure_dirs(ensure_dirs=ensure_dirs)
