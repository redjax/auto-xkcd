"""Entrypoint for the auto-xkcd app's CLI.

Usage:

```python title="auto-xkcd CLI Examples" linenums="1"
## Print available commands
$ cli.py

## Print available pipeline commands
$ cli.py pipelines

## List available pipelines
$ cli.py pipelines list

## Get the current XKCD comic
$ cli.py pipelines get-current

## Loop getting the current XKCD comic, with a 60 second pause between loops
$ cli.py pipelines get-current -c -t 60

## Scrape the XKCD API for missing comics
$ cli.py pipelines scrape

## Loop scraping the XKCD API for missing comics, with a 15 second timeout between loops and a 5 second timeout between http requests.
#  Also overwrite any existing `.msgpack` serialized files.
$ cli.py pipelines scrape -s -l -p 15 -t 5

## Loop scraping the XKCD API for missing comics. Loop a maximum of 5 times
$ cli.py pipelines scrape -l -m 5

## Update the database by loading all serialized comics into XKCDComic objects and saving them,
#  replacing any existing data.
$ cli.py pipelines update-db

## Loop updating the database with a 120s timeout between loops
$ cli.py pipelines update-db -c -t 120
```
"""

from __future__ import annotations

from _cli.groups import pipelines_cli
from _setup import cli_app_setup
import click
from core.dependencies import db_settings, settings
from loguru import logger as log

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
