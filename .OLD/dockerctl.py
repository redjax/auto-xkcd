import argparse
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
import typing as t

## Set paths to docker-compose and .env files
DEV_COMPOSE_FILE: Path = Path("containers/docker-compose.dev.yml")
DEV_COMPOSE_ENV_FILE: Path = Path("containers/env_files/dev.env")
PROD_COMPOSE_FILE: Path = Path("containers/docker-compose.prod.yml")
PROD_COMPOSE_ENV_FILE: Path = Path("containers/env_files/prod.env")

VALID_DEV_ENV_STRINGS: list[str] = ["d", "dev", "development"]
VALID_PROD_ENV_STRINGS: list[str] = ["p", "prod", "production"]
VALID_ENV_STRINGS: list[str] = VALID_DEV_ENV_STRINGS + VALID_PROD_ENV_STRINGS


def validate_path(p: t.Union[str, Path] = None) -> Path:
    assert p, ValueError("Missing a path to validate")
    assert isinstance(p, Path) or isinstance(p, str), TypeError(
        f"p must be a string or Path. Got type: ({type(p)})"
    )

    _path: Path = Path(f"{p}")
    if "~" in f"{_path}":
        _path: Path = Path(f"{_path}").expanduser()

    return _path


def validate_env_str(env_str: str = None) -> str:
    assert env_str, ValueError("Missing an environment string to parse")
    assert isinstance(env_str, str), TypeError(
        f"env_str must be a string. Got type: ({type(env_str)})"
    )

    ## Environment check
    if env_str in VALID_DEV_ENV_STRINGS:
        ## Dev
        env = "dev"

    elif env_str in VALID_PROD_ENV_STRINGS:
        ## Prod
        env = "prod"

    else:
        raise ValueError(
            f"Invalid environment: '{env_str}'. Must be one of {VALID_ENV_STRINGS}"
        )

    return env


@dataclass
class ComposeEnvironmentSpec:
    env_name: str = field(default=None)
    compose_file: t.Union[str, Path] = field(default=None)
    env_file: t.Union[str, Path] = field(default=None)

    def __post_init__(self):  # noqa: D105
        self.env_name = validate_env_str(env_str=self.env_name)
        self.compose_file = validate_path(self.compose_file)
        self.env_file = validate_path(self.env_file)

    def cmd_prefix(self) -> list[str]:
        return ["docker", "compose", "-f", str(self.compose_file)]


DEV_ENV: ComposeEnvironmentSpec = ComposeEnvironmentSpec(
    env_name="dev", compose_file=DEV_COMPOSE_FILE, env_file=DEV_COMPOSE_ENV_FILE
)
PROD_ENV: ComposeEnvironmentSpec = ComposeEnvironmentSpec(
    env_name="prod", compose_file=PROD_COMPOSE_FILE, env_file=PROD_COMPOSE_ENV_FILE
)


def _parse_env(parser: argparse.ArgumentParser = None):
    parser.add_argument(
        "-e",
        "--env",
        choices=VALID_ENV_STRINGS,
        required=True,
        help=f"Environment selection. Development options: {VALID_DEV_ENV_STRINGS}; Production options: {VALID_PROD_ENV_STRINGS}.",
    )


def _add_compose_log_parser(
    subparsers: argparse._SubParsersAction = None,
):
    logs_parser = subparsers.add_parser(
        "logs", help="Follow logs for a container. Must pass a container name."
    )
    ## Add container name requirement
    logs_parser.add_argument(
        "container", metavar="<container_name>", help="Container name"
    )


def _add_compose_attach_parser(subparsers: argparse._SubParsersAction = None):
    attach_parser = subparsers.add_parser(
        "attach", help="Attach to a container. Must pass a container name."
    )
    ## Add container name requirement
    attach_parser.add_argument(
        "container", metavar="<container_name>", help="Container name"
    )


def _add_compose_restart_parser(subparsers: argparse._SubParsersAction = None):
    restart_parser = subparsers.add_parser(
        "restart", help="Restart a container. Must pass a container name."
    )
    ## Add container name requirement
    restart_parser.add_argument(
        "container", metavar="<container_name>", help="Container name"
    )


def _get_compose_spec(env_str: str = None) -> ComposeEnvironmentSpec:
    env_str = validate_env_str(env_str=env_str)
    ## Environment check

    compose_spec: ComposeEnvironmentSpec = PROD_ENV if env_str == "prod" else DEV_ENV

    return compose_spec


def _add_operations_to_subparser(
    subparsers: argparse._SubParsersAction = None,
    operations: list[str] = None,
) -> argparse._SubParsersAction:
    for operation in operations:
        subparsers.add_parser(operation)

    return subparsers


def _add_build_parser(
    subparsers: argparse._SubParsersAction = None,
):
    build_parser = subparsers.add_parser(
        "build", help="Rebuild whole stack or single container"
    )
    ## Add container name requirement
    build_parser.add_argument(
        "container", metavar="<container_name>", nargs="?", help="Container name"
    )
    ## Add optional --no-cache flag
    build_parser.add_argument(
        "--no-cache",
        "-nc",
        action="store_true",
        help="Build without using cache",
    )


def run_cli() -> None:
    ## Create main parser
    parser = argparse.ArgumentParser(
        description="CLI for the auto-xkcd Docker Compose stack."
    )

    ## Add environment selection arg
    _parse_env(parser=parser)

    ## Create subparser for docker-compose commands
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser] = (
        parser.add_subparsers(
            dest="operation", required=True, help="Docker Compose operation to perform."
        )
    )

    ## Create subparser for docker-compose logs commands
    _add_compose_log_parser(subparsers=subparsers)

    ## Create subparser for docker-compose attach commands
    _add_compose_attach_parser(subparsers=subparsers)

    ## Create subparser for docker-compose restart commands
    _add_compose_restart_parser(subparsers=subparsers)

    ## Create subparser for docker-compose build commands
    _add_build_parser(subparsers=subparsers)

    ## Add subarsers main parser
    subparsers = _add_operations_to_subparser(
        subparsers=subparsers,
        operations=["up", "up-build", "down"],
    )

    ## Parse args
    args = parser.parse_args()

    # ## Environment check
    DOCKER_ENV: ComposeEnvironmentSpec = _get_compose_spec(env_str=args.env)
    print(f"Docker Compose environment: {DOCKER_ENV}")

    ## Create command map
    command_map: dict[str, t.Any] = {
        "build": DOCKER_ENV.cmd_prefix() + ["build"],
        "build-nocache": DOCKER_ENV.cmd_prefix() + ["build", "--no-cache"],
        "up": DOCKER_ENV.cmd_prefix() + ["up", "-d"],
        "up-build": DOCKER_ENV.cmd_prefix() + ["up", "-d", "--build"],
        "down": DOCKER_ENV.cmd_prefix() + ["down"],
    }

    ## Detect docker-compose operation
    operation: str = args.operation
    ## Get container name option if operation requires one
    container: str | None = getattr(args, "container", None)

    ## Build docker-compose command
    command = (
        command_map.get(operation)
        if operation not in ["logs", "attach", "restart"]
        else (
            DOCKER_ENV.cmd_prefix() + ["logs", "-f", container]
            if operation == "logs"
            else DOCKER_ENV.cmd_prefix() + [operation, container]
        )
    )

    if not command:
        ## Command not found
        parser.error(message=f"Invalid operation: command '{command}' not found")
    else:
        ## Command found, build and run
        print(f"Running docker-compose command: {' '.join(command)}")

        ## Use subprocess.PIPE/.STDOUT for docker-compose commands
        #  whose output should be tailed
        if operation in ["logs", "attach"]:
            try:
                ## Open subprocess and pipe docker-compose command, leaving open
                with subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    bufsize=1,
                    universal_newlines=True,
                ) as process:
                    ## Print command lines to console
                    for line in process.stdout:
                        print(line, end="")

            ## CTRL-C command detected in pipe
            except KeyboardInterrupt:
                print("\n[CTRL-C detected] Operation interrupted.")
                # process.terminate()  # Terminate the subprocess explicitly

            ## subprocess error
            except subprocess.CalledProcessError as e:
                print(f"Error running command: {e}")

            except Exception as exc:
                err_details: dict = {
                    "exc_type": type(exc),
                    "command": command,
                    "exc_text": exc,
                }
                parser.error(
                    Exception(
                        f"Unhandled exception running command. Details: {err_details}"
                    )
                )
        else:
            ## Any other operation that's not logs or attach

            if operation in ["build", "build-nocache"]:
                ## Append --no-cache flag if specified
                if args.no_cache:
                    command.append("--no-cache")

                if container is None:
                    pass
                else:
                    command.append(container)

            print(f"Running command: {command}")

            try:
                ## Run command
                subprocess.run(command, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error running command: {e}")

            except Exception as exc:
                err_details: dict = {
                    "exc_type": f"{type(exc)}",
                    "command": command,
                    "exc_text": f"{exc}",
                }
                parser.error(
                    Exception(
                        f"Unhandled exception running command. Details: {err_details}"
                    )
                )

            ## Restart container after rebuild
            if operation in ["build", "build-nocache"]:
                if container:
                    print(f"Restarting container {container} after rebuilding")
                    restart_cmd = DOCKER_ENV.cmd_prefix() + ["restart", container]
                    try:
                        subprocess.run(restart_cmd, check=True)
                    except Exception as eexc:
                        err_details: dict = {
                            "exc_type": f"{type(exc)}",
                            "command": command,
                            "container": container,
                            "exc_text": f"{exc}",
                        }


if __name__ == "__main__":
    run_cli()
