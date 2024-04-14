from __future__ import annotations

import time

import click
from core import request_client
from domain.pipelines import PipelineHandler
from domain.xkcd import XKCDComic
from entrypoints import pipeline_entrypoints
import hishel
from loguru import logger as log
from pipelines import pipeline_prefab
from rich.console import Console

console = Console()


@click.command("list")
@click.pass_context
def list_pipelines(ctx) -> None:
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
        click.echo(message=pipeline_str)


@click.command(name="get-current")
@click.pass_context
@click.option(
    "-s",
    "--overwrite-serial",
    is_flag=True,
    help="If get-gurrent is called with -os/--overwrite-serial, any serialized objects will be overwritten if they already exist.",
    default=False,
    show_default=True,
)
@click.option(
    "-c",
    "--continuous",
    is_flag=True,
    help="If True, continuously loop request on an interval.",
    default=False,
    show_default=True,
)
@click.option(
    "-t",
    "--loop-timeout",
    help="Time (in seconds) to pause between loops. Default: 3600 (1 hour).",
    default=3600,
    show_default=True,
)
def get_current_comic(ctx, overwrite_serial: bool, continuous, loop_timeout) -> None:
    loop_timeout: int = int(loop_timeout)
    pipeline_prefab.PIPELINE_CONF_CURRENT_COMIC
    if continuous:
        _loops: int = 1

    else:
        _loops = None

    def start_get_current_comic() -> XKCDComic | None:

        click.echo(message="Getting current XKCD comic")

        with console.status(status="Retrieving comic ...", spinner="dots"):
            # click.echo(f"Getting current XKCD comic ...")
            try:
                current_comic: XKCDComic = (
                    pipeline_entrypoints.start_current_comic_pipeline.run_pipeline(
                        cache_transport=request_client.get_cache_transport(),
                        overwrite_serialized_comic=overwrite_serial,
                    )
                )
                # click.echo(current_comic.telegram_msg)

                return current_comic

            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception while getting current XKCD comic. Details: {exc}"
                )
                log.error(msg)
                log.trace(exc)

    if not continuous:
        current_comic: XKCDComic | None = start_get_current_comic()
        click.echo(message=current_comic.telegram_msg)
    else:
        CONTINUE_LOOP: bool = True

        while CONTINUE_LOOP:
            click.echo(message=f"[Loop count: {_loops}]")

            current_comic: XKCDComic | None = start_get_current_comic()
            click.echo(message=current_comic.telegram_msg)

            with console.status(
                status=f"Pausing for [{loop_timeout}] second(s) between requests ..."
            ):
                time.sleep(loop_timeout)

            _loops += 1


@click.command(name="scrape")
@click.pass_context
@click.option(
    "-t",
    "--request-timeout",
    help="Number of seconds to pause between requests",
    default=5,
    show_default=True,
)
@click.option(
    "-s",
    "--overwrite-serial",
    is_flag=True,
    help="If get-gurrent is called with -os/--overwrite-serial, any serialized objects will be overwritten if they already exist.",
    default=False,
    show_default=True,
)
@click.option(
    "-l",
    "--loop-requests",
    is_flag=True,
    help="Set the scraper to loop when finished.",
    default=False,
    show_default=True,
)
@click.option(
    "-p",
    "--loop-pause",
    help="Number of seconds to pause between loops. Defaults to 3600 (1 hour).",
    default=3600,
    show_default=True,
)
@click.option(
    "-m",
    "--max-loops",
    help="Maximum number of loops before exiting. 0=unlimited, None=1",
    default=None,
    show_default=True,
)
def scrape_missing_comics(
    ctx,
    request_timeout,
    overwrite_serial,
    loop_requests,
    loop_pause,
    max_loops,
) -> None:
    request_timeout: int = int(request_timeout)
    loop_pause: int = int(loop_pause)
    max_loops: int = int(max_loops)

    cache_transport: hishel.CacheTransport = request_client.get_cache_transport()

    def start_scrape() -> list[XKCDComic]:
        _status = "Scraping missing comics"
        with console.status(status=f"{_status} ..."):
            scraped_comics: list[XKCDComic] = (
                pipeline_entrypoints.start_scrape_missing_pipeline.run_pipeline(
                    cache_transport=cache_transport,
                    request_sleep=request_timeout,
                    overwrite_serialized_comic=overwrite_serial,
                )
            )

        if scraped_comics is None or len(scraped_comics) == 0:
            click.echo(message="No comics were scraped. Have all comics been saved?")
            return []

        click.echo(message=f"Scraped [{len(scraped_comics)}] comic(s).")
        if len(scraped_comics) < 5:
            for c in scraped_comics:
                click.echo(
                    message=f"Scraped comic: ${c.num} - {c.title}. Link: {c.img_url}"
                )

        return scraped_comics

    _loops: int = 1
    click.echo(message="Starting scrape for missing comics.")

    if max_loops is None:
        _scrape = start_scrape()
        click.echo(message="Finished scrape.")

    elif max_loops == 0:
        click.echo(message=f"[Loop count: {_loops}]")

        CONTINUE_LOOP: bool = True

        while CONTINUE_LOOP:
            _scrape = start_scrape()
            click.echo(message=f"Scraped [({len(_scrape)})] comic(s).")

            with console.status(
                status=f"Sleeping for [{loop_pause}] second(s) between scrapes ..."
            ):
                time.sleep(loop_pause)

    else:
        while _loops <= max_loops:
            click.echo(message=f"Loop [{_loops}/{max_loops}]")

            _scrape: list[XKCDComic] = start_scrape()
            click.echo(message=f"Scraped [({len(_scrape)})] comic(s)")

            _loops += 1

            if _loops <= max_loops:
                with console.status(
                    status=f"Sleeping for [{loop_pause}] second(s) between scrapes ..."
                ):
                    time.sleep(loop_pause)

        click.echo(message=f"Finished scraping after [{_loops}] loop(s)")


@click.command(name="update-db")
@click.pass_context
@click.option(
    "-s",
    "--overwrite-serial",
    is_flag=True,
    help="If get-gurrent is called with -os/--overwrite-serial, any serialized objects will be overwritten if they already exist.",
    default=False,
    show_default=True,
)
@click.option(
    "-c",
    "--continuous",
    is_flag=True,
    help="If True, continuously loop request on an interval.",
    default=False,
    show_default=True,
)
@click.option(
    "-t",
    "--loop-timeout",
    help="Time (in seconds) to pause between loops. Default: 3600 (1 hour).",
    default=3600,
    show_default=True,
)
def update_database(ctx, overwrite_serial, continuous, loop_timeout) -> None:
    loop_timeout: int = int(loop_timeout)

    if continuous:
        _loops: int = 1
    else:
        _loops: int = None

    def start_update_db():
        click.echo(message="Updating database from serialized XKCDComic objects")

        _status = "Deserializing comics & saving to database"
        log.debug(f"Status")
        with console.status(status=f"{_status} ..."):
            pipeline_entrypoints.start_save_serialized_comics_to_db_pipeline.run_pipeline()

        click.echo(message="Database updated.")

    if not continuous:
        start_update_db()
    else:
        CONTINUE_LOOP: bool = True

        while CONTINUE_LOOP:
            start_update_db()

            with console.status(
                status=f"Waiting [{loop_timeout}] second(s) between DB updates ..."
            ):
                time.sleep(loop_timeout)

            continue
