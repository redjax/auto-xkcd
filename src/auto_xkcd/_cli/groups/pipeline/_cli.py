from .commands import (
    list_pipelines,
    get_current_comic,
    scrape_missing_comics,
    update_database,
)

import click
from loguru import logger as log


@click.group("pipelines")
@click.pass_context
def pipelines_cli(ctx):
    pass


## Add imported pipelines to pipelines_cli click group
pipelines_cli.add_command(list_pipelines)
pipelines_cli.add_command(get_current_comic)
pipelines_cli.add_command(scrape_missing_comics)
pipelines_cli.add_command(update_database)