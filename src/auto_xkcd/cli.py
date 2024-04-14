from core.dependencies import settings, db_settings
from _setup import cli_app_setup
from _cli.groups import pipelines_cli

from loguru import logger as log
import click


## CLI command groups in this list will be added to the main CLI group
ENABLED_COMMAND_GROUPS: list[click.Group] = [pipelines_cli]


@click.group("cli")
@click.pass_context
def cli_main(ctx):
    pass


for _group in ENABLED_COMMAND_GROUPS:
    cli_main.add_command(_group)

# cli_main.add_command(pipelines_cli)

if __name__ == "__main__":
    cli_app_setup(_settings=settings, db_settings=db_settings)

    cli_main()
