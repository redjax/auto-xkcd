"""Run prefab docker-compose commands with a simple interface.

Run long docker commands like: docker-compose -f containers/docker-compose.*.yml [up|build|down]
"""

import os
from contextlib import contextmanager, AbstractContextManager
from dataclasses import dataclass, field
import typing as t
from pathlib import Path
import subprocess

DEV_COMPOSE_FILE: Path = Path("containers/docker-compose.dev.yml")
DEV_COMPOSE_ENV_FILE: Path = Path("containers/env_files/dev.env")
PROD_COMPOSE_FILE: Path = Path("containers/docker-compose.prod.yml")
PROD_COMPOSE_ENV_FILE: Path = Path("containers/env_files/prod.env")

dev_compose_dict: dict = {
    "env": "dev",
    "compose_file": DEV_COMPOSE_FILE,
    "compose_env_file": DEV_COMPOSE_ENV_FILE,
}

prod_compose_dict: dict = {
    "env": "prod",
    "compose_file": PROD_COMPOSE_FILE,
    "compose_env_file": PROD_COMPOSE_ENV_FILE,
}


@dataclass
class ComposeFileMeta:
    env: str = field(default="prod")
    compose_file: Path = field(default=None)
    compose_env_file: Path = field(default=None)

    @property
    def compose_f_param(self) -> list[str]:
        """Return ["-f", f"{self.compose_file}]."""
        return ["-f", f"{self.compose_file}"]

    def cmd_str_prefix(self) -> list[str]:
        return ["docker", "compose"] + self.compose_f_param


DEV_COMPOSE: ComposeFileMeta = ComposeFileMeta(**dev_compose_dict)
PROD_COMPOSE: ComposeFileMeta = ComposeFileMeta(**prod_compose_dict)


def clear() -> None:
    cmd = "cls" if os.name == "nt" else "clear"
    os.system(cmd)


def prompt_env(loop_msg: str = None) -> str:
    clear()

    try:
        if loop_msg:
            print(loop_msg)

        choice = input("> Which environment [options: (d)ev|(p)rod]?: ").lower()

        if choice in ["d", "dev"]:
            choice = "dev"
        elif choice in ["p", "prod"]:
            choice = "prod"

        if choice not in ["dev", "prod"]:
            msg = ValueError(
                f"[ERROR] Invalid choice: {choice}. Must be one of ['dev', 'prod']"
            )

            choice = prompt_env(loop_msg=msg)

        return choice

    except Exception as exc:
        msg = Exception(f"Unhandled exception parsing user input. Details: {exc}")
        print(f"[ERROR] {msg}")

        raise msg


class ComposeCLIContext(AbstractContextManager):
    def __init__(  # noqa: D107
        self, compose_meta: ComposeFileMeta, env: str | None = None
    ):  # noqa: D107
        self.compose_meta = compose_meta
        # self.env = env
        self.proc = None

    def __enter__(self):  # noqa: D105
        choice = self.get_choice()

        self.choice = choice
        if choice == "5":
            self.prompt_container_name()

        return self

    def __exit__(self, exc_type, exc_value, traceback):  # noqa: D105
        pass

    def prompt_container_name(self):
        self.container_name = input("Enter container name: ")

    # def prompt_compose_env(self) -> str:
    #     if self.env:
    #         return self

    #     _env = prompt_env()
    #     self.env = _env

    #     return self

    def get_choice(self, loop_msg: str = None):
        # if not self.env:
        #     prompt_env()

        def print_menu() -> None:
            print(f"[env:{self.compose_meta.env}] Docker Compose CLI\n")
            print("Choose an option:")
            print("1: docker compose build")
            print("2: docker compose build --no-cache")
            print("3: docker compose up -d")
            print("4: docker compose up -d --build")
            # print("5: docker compose logs -f <container_name>")
            print(
                "5: docker compose up -d --build && docker compose logs -f <container_name>"
            )

            print("")
            print("a: attach (for viewing live CLI of container)")
            print("d: docker compose down")
            print("l: docker compose logs -f <container_name>")
            print("r: docker compose restart <container_name>")
            print("\nq: quit")

        valid_choices: list[str] = ["1", "2", "3", "4", "5", "a", "l", "d", "r"]

        clear()

        print_menu()

        if loop_msg:
            print(loop_msg)

        _choice: str = input("\n> Choice: ")

        if _choice == "q":
            print("Quitting.")
            exit(0)

        while _choice not in valid_choices:
            msg = ValueError(f"Invalid choice: {_choice}")
            print(f"[ERROR] {msg}")
            _choice = self.get_choice(loop_msg=msg)

        return _choice

    def _build(self, with_cache: bool = True) -> list[str]:
        cmd: list[str] = self.compose_meta.cmd_str_prefix() + [
            "build",
        ]

        if not with_cache:
            cmd = cmd + ["--no-cache"]

        return cmd

    def _up(self, build: bool = False) -> list[str]:
        cmd: list[str] = self.compose_meta.cmd_str_prefix() + ["up", "-d"]

        if build:
            cmd = cmd + ["--build"]

        return cmd

    def _restart(self) -> list[str]:
        cmd: list[str] = self.compose_meta.cmd_str_prefix() + [
            "restart",
            self.container_name,
        ]

        return cmd

    def _logs(self) -> list[str]:
        cmd: list[str] = self.compose_meta.cmd_str_prefix() + [
            "logs",
            "-f",
            self.container_name,
        ]

        return cmd

    def _attach(self) -> None:
        cmd: list[str] = self.compose_meta.cmd_str_prefix() + [
            "attach",
            self.container_name,
        ]

        return cmd

    def _down(self) -> list[str]:
        cmd: list[str] = self.compose_meta.cmd_str_prefix() + ["down"]

        return cmd

    def run_command(self):
        match self.choice:
            case "1":
                command: list[str] = self._build()
            case "2":
                command = self._build(with_cache=False)
            case "3":
                command = self._up()
            case "4":
                command = self._up(build=True)
            case "5":
                if not hasattr(self, "container_name"):
                    self.container_name = input("Enter container name: ")
                command = self._up(build=True)
                command = self._logs()
            case "a":
                if not hasattr(self, "container_name"):
                    self.container_name = input("Enter container name: ")
                command = self._attach()
            case "d":
                command = self._down()
            case "l":
                if not hasattr(self, "container_name"):
                    self.container_name = input("Enter container name: ")
                command = self._logs()
            case "r":
                if not hasattr(self, "container_name"):
                    self.container_name = input("Enter container name: ")
                command = self._restart()
            case _:
                raise ValueError(f"Invalid choice: {self.choice}")

        print(f"Docker command: {command}")
        try:
            subprocess.run(command)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception running command '{command}'. Details: {exc}"
            )
            print(f"[ERROR] {msg}")

            return


def main(env: str = None):
    if not env:
        env: str = prompt_env()

    match env:
        case "prod":
            compose_meta: ComposeFileMeta = PROD_COMPOSE
        case "dev":
            compose_meta: ComposeFileMeta = DEV_COMPOSE
        case _:

            raise ValueError(f"Unknown env: {env}")

    with ComposeCLIContext(compose_meta=compose_meta) as ctx:
        ctx.run_command()


if __name__ == "__main__":
    env: str = prompt_env()
    main(env=env)
