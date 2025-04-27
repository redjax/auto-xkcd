from __future__ import annotations

from datetime import timedelta
from pathlib import Path
import shutil
import typing as t

from core_utils import time_utils
from cyclopts import App, Group, Parameter
from loguru import logger as log

__all__ = ["setup_app"]

setup_app = App(name="setup", help="CLI for project setup")


@setup_app.command(name="app-config-files")
def setup_config_files():
    config_toml_files: list[Path] = [
        p for p in Path("config").rglob("**/*.toml") if p.is_file()
    ]
    log.debug(f"Found ({len(config_toml_files)}) TOML config file(s) in path 'config/'")

    successes: list[dict] = []
    failures: list[dict] = []

    for config_toml in config_toml_files:
        log.debug(f"Config .toml: {config_toml}")

        local_config_file = config_toml.with_stem(config_toml.stem + ".local")
        log.debug(
            f".local config: {local_config_file} (exists: {Path(local_config_file).exists()})"
        )

        metadata = {"orig": config_toml, "copy": local_config_file}

        if not Path(local_config_file).exists():
            log.info(f"Creating .local config file: {local_config_file}")
            # Path(local_config_file).touch()
            try:
                shutil.copy2(src=config_toml, dst=local_config_file)
                log.info(f"Copied '{config_toml}' to '{local_config_file}'")

                successes.append(metadata)
            except Exception as exc:
                msg = f"({type(exc)}) Error copying '{config_toml}' to '{local_config_file}'. Details: {exc}"
                log.error(msg)

                failures.append(metadata)
                continue
        else:
            log.debug(
                f"Skip copying '{config_toml}' to '{local_config_file}', .local version already exists"
            )
            continue

    log.info(f"Copied [{len(successes)}] config file(s) to .local version")
    if len(failures) > 0:
        log.warning(
            f"Failed to copy [{len(failures)}] config file(s) to .local version. Failures:\n{failures}"
        )
