import threading

from core import request_client
from domain.pipelines import PipelineHandler
from domain.xkcd import XKCDComic
from entrypoints import pipeline_entrypoints
from pipelines import pipeline_prefab

import click
from loguru import logger as log

from rich.console import Console

console = Console()


@click.command("list")
@click.pass_context
def list_pipelines(ctx):
    AVAILABLE_PIPELINES: list[PipelineHandler] = [
        pipeline_prefab.PIPELINE_CONF_CURRENT_COMIC,
        pipeline_prefab.PIPELINE_CONF_SAVE_SERIALIZED_TO_DB,
        pipeline_prefab.PIPELINE_CONF_SCRAPE_MISSING_COMICS,
    ]

    for _pipeline in AVAILABLE_PIPELINES:
        pipeline_str: str = f"""
Pipeline name: {_pipeline.name}
Pipeline method: {_pipeline.method.__name__}
Pipeline kwargs: {_pipeline.kwargs}
"""

        click.echo(f"[PIPELINE: {_pipeline.name}]")
        click.echo(pipeline_str)


@click.command("get-current")
@click.pass_context
@click.option(
    "-s",
    "--overwrite-serial",
    is_flag=True,
    help="If get-gurrent is called with -os/--overwrite-serial, any serialized objects will be overwritten if they already exist.",
    default=False,
    show_default=True,
)
def get_current_comic(ctx, overwrite_serial: bool):
    pipeline_prefab.PIPELINE_CONF_CURRENT_COMIC

    click.echo("Getting current XKCD comic")

    with console.status("Retrieving comic ...", spinner="dots"):
        # click.echo(f"Getting current XKCD comic ...")
        try:
            current_comic: XKCDComic = (
                pipeline_entrypoints.start_current_comic_pipeline.run_pipeline(
                    cache_transport=request_client.get_cache_transport(),
                    overwrite_serialized_comic=overwrite_serial,
                )
            )
            # click.echo(current_comic.telegram_msg)

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception while getting current XKCD comic. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

    click.echo(current_comic.telegram_msg)


@click.command("scrape")
@click.pass_context
@click.argument(
    "timeout",
    # help="Number of seconds to pause between requests",
    default=0,
    # show_default=True,
)
@click.option(
    "-s",
    "--overwrite-serial",
    is_flag=True,
    help="If get-gurrent is called with -os/--overwrite-serial, any serialized objects will be overwritten if they already exist.",
    default=False,
    show_default=True,
)
def scrape_missing_comics(ctx, timeout, overwrite_serial):
    cache_transport = request_client.get_cache_transport()

    click.echo("Starting scrape for missing comics.")

    with console.status("Scraping missing comics ..."):
        scraped_comics: list[XKCDComic] = (
            pipeline_entrypoints.start_scrape_missing_pipeline.run_pipeline(
                cache_transport=cache_transport,
                request_sleep=timeout,
                overwrite_serialized_comic=overwrite_serial,
            )
        )

    if scraped_comics is None or len(scraped_comics) == 0:
        click.echo("No comics were scraped. Have all comics been saved?")
        return

    click.echo(f"Scraped [{len(scraped_comics)}] comic(s).")
    if len(scraped_comics) < 5:
        for c in scraped_comics:
            click.echo(f"Scraped comic: ${c.num} - {c.title}. Link: {c.img_url}")


@click.command("update-db")
@click.pass_context
@click.option(
    "-s",
    "--overwrite-serial",
    is_flag=True,
    help="If get-gurrent is called with -os/--overwrite-serial, any serialized objects will be overwritten if they already exist.",
    default=False,
    show_default=True,
)
def update_database(ctx, overwrite_serial):
    click.echo("Updating database from serialized XKCDComic objects")

    with console.status("Deserializing comics & saving to database ..."):
        pipeline_entrypoints.start_save_serialized_comics_to_db_pipeline.run_pipeline()

    click.echo("Database updated.")
