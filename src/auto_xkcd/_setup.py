"""Methods meant to be called early during execution.

Handle setup tasks, like creating directories that must exist, initializing logging, etc.

"""

from __future__ import annotations

from pathlib import Path
from sqlite3 import OperationalError

from core import database
from core.config import AppSettings, DBSettings
from core.dependencies import settings
from core.paths import ENSURE_DIRS
from helpers import cli_helpers
import ibis
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
    log.debug(f"Creating base directory/ies")
    try:
        path_utils.ensure_dirs_exist(ensure_dirs=ensure_dirs)
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception ensuring directories exist. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc


def setup_ibis_interactive(interactive: bool = True):
    log.debug(f"Setting ibis.options.interactive to '{interactive}'.")
    ibis.options.interactive = True


def setup_database(db_settings: DBSettings = None):
    db_settings.echo = True

    log.debug(f"DB setting: {db_settings}")

    log.info("Creating Base metadata")
    try:
        database.create_base_metadata(
            base=database.Base, engine=db_settings.get_engine()
        )
    except PermissionError as perm_exc:
        msg = Exception(
            f"Permission denied creating Base metadata. Details: {perm_exc}"
        )
        log.error(msg)
        log.trace(perm_exc)

        raise perm_exc
    except OperationalError as op_err:
        msg = Exception(
            f"SQLite operational error occurred while creating Base metadata. Details: {op_err}"
        )
        log.error(msg)
        log.trace(op_err)

        raise op_err
    except Exception as exc:
        msg = Exception(f"Unhandled exception creating Base metadata. Details: {exc}")
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

    match settings.env:
        case ["dev", "notebook"]:
            setup_ibis_interactive(interactive=True)
        case "prod":
            setup_ibis_interactive(interactive=False)


def cli_app_setup(
    _settings: AppSettings = None,
    db_settings: DBSettings = None,
    ensure_dirs: list[Path] = ENSURE_DIRS,
    log_level: str = "ERROR",
):
    # _settings.env = "cli"
    _settings.log_level = log_level

    cli_logger_sinks: list = [
        # sinks.LoguruSinkStdErr(level=settings.log_level).as_dict(),
        sinks.LoguruSinkStdOut(level=settings.log_level).as_dict(),
        sinks.LoguruSinkAppFile(sink=f"{settings.logs_dir}/cli/app.log").as_dict(),
        sinks.LoguruSinkErrFile(sink=f"{settings.logs_dir}/cli/err.log").as_dict(),
        sinks.LoguruSinkTraceFile(sink=f"{settings.logs_dir}/cli/trace.log").as_dict(),
    ]

    init_logger(sinks=cli_logger_sinks)
    log.info(f"Logging initialized")

    setup_ensure_dirs(ensure_dirs=ensure_dirs)

    setup_database(db_settings=db_settings)

    ## Set echo to False after database initialization
    db_settings.echo = False

    ## Clear screen
    cli_helpers.clear()
