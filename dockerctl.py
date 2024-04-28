import typing as t
import argparse
import subprocess
from pathlib import Path
from dataclasses import dataclass, field

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


def validate_parser_obj(
    parser: argparse.ArgumentParser = None,
) -> argparse.ArgumentParser:
    assert parser, ValueError("Missing an arg parser")
    assert isinstance(parser, argparse.ArgumentParser), TypeError(
        f"parser must be of type argparse.ArgumentParser. Got type: ({type(parser)})"
    )

    return parser


def validate_subparser_obj(
    subparser: argparse._SubParsersAction = None,
) -> argparse._SubParsersAction:
    assert subparser, ValueError("Missing a subparser object.")
    assert isinstance(subparser, argparse._SubParsersAction), TypeError(
        f"subparser must be of type _SubParsersAction[ArgumentParser]. Got type: ({type(subparser)})"
    )

    return subparser


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
    parser = validate_parser_obj(parser=parser)
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
    subparsers = validate_subparser_obj(subparser=subparsers)

    logs_parser = subparsers.add_parser(
        "logs", help="Follow logs for a container. Must pass a container name."
    )
    ## Add container name requirement
    logs_parser.add_argument(
        "container", metavar="<container_name>", help="Container name"
    )


def _add_compose_attach_parser(subparsers: argparse._SubParsersAction = None):
    subparsers = validate_subparser_obj(subparser=subparsers)

    attach_parser = subparsers.add_parser(
        "attach", help="Attach to a container. Must pass a container name."
    )
    ## Add container name requirement
    attach_parser.add_argument(
        "container", metavar="<container_name>", help="Container name"
    )


def _add_compose_restart_parser(subparsers: argparse._SubParsersAction = None):
    subparsers = validate_subparser_obj(subparser=subparsers)

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
    subparsers = validate_subparser_obj(subparser=subparsers)

    for operation in operations:
        subparsers.add_parser(operation)

    return subparsers


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

    ## Add subarsers main parser
    subparsers = _add_operations_to_subparser(
        subparsers=subparsers,
        operations=["build", "build-nocache", "up", "up-build", "down"],
    )

    ## Parse args
    try:
        args = parser.parse_args()
    except Exception as exc:
        parser.error(Exception(f"Error while parsing args. Details: {exc}"))

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

    ## An operation requiring a container name was selected, but no container name was passed
    if operation in ["logs", "attach", "restart"] and not container:
        parser.error(f"Operation '{operation}' requires a container name")

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
            try:
                ## Run command
                subprocess.run(command, check=True)
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


if __name__ == "__main__":
    run_cli()
