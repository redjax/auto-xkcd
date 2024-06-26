from __future__ import annotations

import typing as t
from pathlib import Path
import platform
import shutil

import nox

from dataclasses import dataclass, field

nox.options.default_venv_backend = "venv"
nox.options.reuse_existing_virtualenvs = True
nox.options.error_on_external_run = False
nox.options.error_on_missing_interpreters = False
# nox.options.report = True

## Define sessions to run when no session is specified
nox.sessions = ["lint", "export", "tests"]


@dataclass
class CopyFileDefinition:
    src: t.Union[str, Path] = field(default=None)
    dst: t.Union[str, Path] = field(default=None)

    def __post_init__(self):  # noqa: D105
        try:
            self.src = Path(f"{self.src}")
        except Exception as exc:
            raise Exception(
                f"Unhandled exception converting src to Path. Details: {exc}"
            )

        try:
            self.dst = Path(f"{self.dst}")
        except Exception as exc:
            raise Exception(
                f"Unhandled exception converting dst to Path. Details: {exc}"
            )


# INIT_COPY_FILES: list[dict[str, str]] = [
#     ## App config
#     {"src": "config/.secrets.example.toml", "dest": "config/.secrets.toml"},
#     {"src": "config/settings.toml", "dest": "config/settings.local.toml"},
#     {"src": "config/db/settings.toml", "dest": "config/db/settings.local.toml"},
#     {"src": "config/db/settings.secrets", "dest": "config/db/.secrets.local.toml"},
#     {"src": "config/minio/.secrets.example.toml", "dest": "config/minio/.secrets.toml"},
#     {"src": "config/minio/settings.toml", "dest": "config/minio/settings.local.toml"},
#     {"src": "config/celery/settings.toml", "dest": "config/celery/settings.local.toml"},
#     ## Compose env files
#     {
#         "src": "containers/env_files/dev.example.env",
#         "dest": "containers/env_files/dev.env",
#     },
#     {
#         "src": "containers/env_files/prod.example.env",
#         "dest": "containers/env_files/prod.env",
#     },
#     {
#         "src": "containers/devcontainers/minio/.env.example",
#         "dest": "containers/devcontainers/minio/.env",
#     },
# ]

INIT_COPY_FILES: list[CopyFileDefinition] = [
    ## App config
    CopyFileDefinition(src="config/.secrets.example.toml", dst="config/.secrets.toml"),
    CopyFileDefinition(src="config/settings.toml", dst="config/settings.local.toml"),
    CopyFileDefinition(
        src="config/db/settings.toml", dst="config/db/settings.local.toml"
    ),
    CopyFileDefinition(
        src="config/db/.secrets.toml", dst="config/db/.secrets.local.toml"
    ),
    CopyFileDefinition(
        src="config/minio/.secrets.example.toml", dst="config/minio/.secrets.toml"
    ),
    CopyFileDefinition(
        src="config/minio/settings.toml", dst="config/minio/settings.local.toml"
    ),
    CopyFileDefinition(
        src="config/celery/settings.toml", dst="config/celery/settings.local.toml"
    ),
    ## Compose env files
    CopyFileDefinition(
        src="containers/env_files/dev.example.env",
        dst="containers/env_files/dev.env",
    ),
    CopyFileDefinition(
        src="containers/env_files/prod.example.env",
        dst="containers/env_files/prod.env",
    ),
    CopyFileDefinition(
        src="containers/devcontainers/minio/.env.example",
        dst="containers/devcontainers/minio/.env",
    ),
]

INIT_MKDIRS: list[Path] = [
    Path("containers/env_files"),
    Path("containers/containers/devcontainers"),
    Path("containers/container_data"),
    Path("containers/container_data/dev"),
    Path("containers/container_data/prod"),
]
# INIT_TOUCH_FILES: list[dict[str, Path]] = [
#     {"path": Path("./testfile.txt"), "content": "This is a minio test file."}
# ]
INIT_TOUCH_FILES: list[dict[str, Path]] = []
## Define versions to test
PY_VERSIONS: list[str] = ["3.12", "3.11"]
## Set PDM version to install throughout
PDM_VER: str = "2.11.2"
## Set paths to lint with the lint session
LINT_PATHS: list[str] = ["src", "tests", "./noxfile.py"]

## Get tuple of Python ver ('maj', 'min', 'mic')
PY_VER_TUPLE = platform.python_version_tuple()
## Dynamically set Python version
DEFAULT_PYTHON: str = f"{PY_VER_TUPLE[0]}.{PY_VER_TUPLE[1]}"

## Set directory for requirements.txt file output
REQUIREMENTS_OUTPUT_DIR: Path = Path("./requirements")
## Ensure REQUIREMENTS_OUTPUT_DIR path exists
if not REQUIREMENTS_OUTPUT_DIR.exists():
    try:
        REQUIREMENTS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        msg = Exception(
            f"Unable to create requirements export directory: '{REQUIREMENTS_OUTPUT_DIR}'. Details: {exc}"
        )
        print(msg)

        REQUIREMENTS_OUTPUT_DIR: Path = Path(".")


@nox.session(python=PY_VERSIONS, name="build-env")
@nox.parametrize("pdm_ver", [PDM_VER])
def setup_base_testenv(session: nox.Session, pdm_ver: str):
    print(f"Default Python: {DEFAULT_PYTHON}")
    session.install(f"pdm>={pdm_ver}")

    print("Installing dependencies with PDM")
    session.run("pdm", "sync")
    session.run("pdm", "install")


@nox.session(python=[DEFAULT_PYTHON], name="lint")
def run_linter(session: nox.Session):
    session.install("ruff", "black")

    for d in LINT_PATHS:
        if not Path(d).exists():
            print(f"Skipping lint path '{d}', could not find path")
            pass
        else:
            lint_path: Path = Path(d)
            print(f"Running ruff imports sort on '{d}'")
            session.run(
                "ruff",
                "--select",
                "I",
                "--fix",
                lint_path,
            )

            print(f"Formatting '{d}' with Black")
            session.run(
                "black",
                lint_path,
            )

            print(f"Running ruff checks on '{d}' with --fix")
            session.run(
                "ruff",
                "--config",
                "ruff.ci.toml",
                lint_path,
                "--fix",
            )


@nox.session(python=[DEFAULT_PYTHON], name="export")
@nox.parametrize("pdm_ver", [PDM_VER])
def export_requirements(session: nox.Session, pdm_ver: str):
    session.install(f"pdm>={pdm_ver}")

    print("Exporting production requirements")
    session.run(
        "pdm",
        "export",
        "--prod",
        "-o",
        f"{REQUIREMENTS_OUTPUT_DIR}/requirements.txt",
        "--without-hashes",
    )

    print("Exporting development requirements")
    session.run(
        "pdm",
        "export",
        "-d",
        "-o",
        f"{REQUIREMENTS_OUTPUT_DIR}/requirements.dev.txt",
        "--without-hashes",
    )

    print("Exporting docs requirements")
    session.run(
        "pdm",
        "export",
        "-G",
        "docs",
        "--no-default",
        "-o",
        "docs/requirements.txt",
        "--without-hashes",
    )

    # print("Exporting CI requirements")
    # session.run(
    #     "pdm",
    #     "export",
    #     "--group",
    #     "ci",
    #     "-o",
    #     f"{REQUIREMENTS_OUTPUT_DIR}/requirements.ci.txt",
    #     "--without-hashes",
    # )


@nox.session(python=PY_VERSIONS, name="tests")
@nox.parametrize("pdm_ver", [PDM_VER])
def run_tests(session: nox.Session, pdm_ver: str):
    session.install(f"pdm>={pdm_ver}")
    session.run("pdm", "install")

    print("Running Pytest tests")
    session.run(
        "pdm",
        "run",
        "pytest",
        "-n",
        "auto",
        "--tb=auto",
        "-v",
        "-rsXxfP",
    )


@nox.session(python=DEFAULT_PYTHON, name="pre-commit-all")
def run_pre_commit_all(session: nox.Session):
    session.install("pre-commit")
    session.run("pre-commit")

    print("Running all pre-commit hooks")
    session.run("pre-commit", "run")


@nox.session(python=DEFAULT_PYTHON, name="pre-commit-update")
def run_pre_commit_autoupdate(session: nox.Session):
    session.install(f"pre-commit")

    print("Running pre-commit autoupdate")
    session.run("pre-commit", "autoupdate")


@nox.session(python=DEFAULT_PYTHON, name="pre-commit-nbstripout")
def run_pre_commit_nbstripout(session: nox.Session):
    session.install(f"pre-commit")

    print("Running nbstripout pre-commit hook")
    session.run("pre-commit", "run", "nbstripout")


# @nox.session(python=DEFAULT_PYTHON, name="init-setup")
# def run_initial_setup(session: nox.Session):
#     if INIT_MKDIRS is None:
#         print(f"INIT_MKDIRS is empty. Skipping.")
#         pass

#     else:
#         for d in INIT_MKDIRS:
#             if not d.exists():
#                 try:
#                     d.mkdir(parents=True, exist_ok=True)
#                 except Exception as exc:
#                     msg = Exception(
#                         f"Unhandled exception creating directory '{d}'. Details: {exc}"
#                     )
#                     print(f"[ERROR] {msg}")

#                     pass

#     if INIT_COPY_FILES is None:
#         print(f"INIT_COPY_FILES is empty. Skipping")
#         pass

#     else:

#         for pair_dict in INIT_COPY_FILES:
#             src = Path(pair_dict["src"])
#             dest = Path(pair_dict["dest"])
#             if not dest.exists():
#                 print(f"Copying {src} to {dest}")
#                 try:
#                     shutil.copy(src, dest)
#                 except Exception as exc:
#                     msg = Exception(
#                         f"Unhandled exception copying file from '{src}' to '{dest}'. Details: {exc}"
#                     )
#                     print(f"[ERROR] {msg}")

#     if INIT_TOUCH_FILES is None:
#         print(f"INIT_TOUCH_FILES is empty. Skipping.")
#         pass
#     else:
#         for f_dict in INIT_TOUCH_FILES:
#             if not f_dict["path"].exists():
#                 try:
#                     with open(f_dict["path"], "w") as f:
#                         f.write(f_dict["content"])
#                 except Exception as exc:
#                     msg = Exception(
#                         f"Unhandled exception creating file '{f_dict['path']}. Details: {exc}"
#                     )
#                     print(f"[ERROR] {msg}")

#                     raise msg


@nox.session(python=DEFAULT_PYTHON, name="init-setup")
def run_initial_setup(session: nox.Session):
    if INIT_MKDIRS is None:
        print(f"INIT_MKDIRS is empty. Skipping.")
        pass

    else:
        for d in INIT_MKDIRS:
            if not d.exists():
                try:
                    d.mkdir(parents=True, exist_ok=True)
                except Exception as exc:
                    msg = Exception(
                        f"Unhandled exception creating directory '{d}'. Details: {exc}"
                    )
                    print(f"[ERROR] {msg}")

                    pass

    if INIT_COPY_FILES is None:
        print(f"INIT_COPY_FILES is empty. Skipping")
        pass

    else:

        for pair in INIT_COPY_FILES:
            if not pair.dst.exists():
                print(f"Copying {pair.src} to {pair.dst}")

                try:
                    shutil.copy(pair.src, pair.dst)
                except Exception as exc:
                    msg = Exception(
                        f"Unhandled exception copying file from '{pair.src}' to '{pair.dst}'. Details: {exc}"
                    )
                    print(f"[ERROR] {msg}")

    if INIT_TOUCH_FILES is None:
        print(f"INIT_TOUCH_FILES is empty. Skipping.")
        pass
    else:
        for f_dict in INIT_TOUCH_FILES:
            if not f_dict["path"].exists():
                try:
                    with open(f_dict["path"], "w") as f:
                        f.write(f_dict["content"])
                except Exception as exc:
                    msg = Exception(
                        f"Unhandled exception creating file '{f_dict['path']}. Details: {exc}"
                    )
                    print(f"[ERROR] {msg}")

                    raise msg


@nox.session(python=DEFAULT_PYTHON, name="new-dynaconf-config")
def create_new_dynaconf_config(session: nox.session):
    CONFIG_ROOT: str = "config"

    def prompt_config_name(config_root: str = CONFIG_ROOT) -> str:
        try:
            new_conf: str = input(f"New config path: {config_root}/")
            return f"{CONFIG_ROOT}/{new_conf}"

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception getting new config path. Details: {exc}"
            )
            print(f"[ERROR] {msg}")

            raise exc

    init_files: list[str] = [
        ".secrets.toml",
        ".secrets.example.toml",
        "settings.toml",
        "settings.local.toml",
    ]
    new_file_contents: str = f"[default]\n\n[dev]\n\n[prod]\n"
    config_dir: str = prompt_config_name()

    if not Path(config_dir).exists():
        print(f"Creating path '{config_dir}'")
        try:
            Path(config_dir).mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception creating path '{config_dir}'. Details: {exc}"
            )
            print(f"[ERROR] {msg}")

            raise exc

    for f in init_files:
        f_path: Path = Path(f"{config_dir}/{f}")

        if not f_path.exists():
            print(f"Creating file '{f_path}'")

            try:
                with open(f_path, "w") as _f:
                    _f.write(new_file_contents)
            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception creating file '{f_path}'. Details: {exc}"
                )
                print(f"[ERROR] {msg}")

                raise exc
