from __future__ import annotations

from .methods import _get_current, _get_multiple, _list_missing_comic_imgs

from core.constants import IGNORE_COMIC_NUMS
import hishel
from loguru import logger as log
from modules import xkcd_mod
from packages import xkcd
from packages.xkcd.comic.img import save_img


def pipeline_get_current_comic(
    cache_transport: hishel.CacheTransport = None, force_live_request: bool = False
) -> xkcd_mod.XKCDComic:
    assert cache_transport, ValueError("Missing cache transport for request client")

    try:
        current_comic: xkcd_mod.XKCDComic = _get_current(
            cache_transport=cache_transport, force_live_request=force_live_request
        )

        return current_comic

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting current XKCD comic. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc


def pipeline_get_multiple_comics(
    cache_transport: hishel.CacheTransport = None,
    comic_nums: list[int] = None,
    force_live_request: bool = False,
    request_sleep: int = 5,
) -> list[xkcd_mod.XKCDComic]:
    assert cache_transport, ValueError("Missing cache transport for request client")
    assert comic_nums, ValueError("Missing list of comic numbers to scrape")

    if force_live_request:
        raise NotImplementedError(
            f"Forcing a live request on multiple comics not yet supported."
        )

    try:
        comics: list[xkcd_mod.XKCDComic] = _get_multiple(
            cache_transport=cache_transport,
            comic_nums=comic_nums,
            request_sleep=request_sleep,
        )

    except Exception as exc:
        msg = Exception(f"Unhandled exception scraping multiple comics. Details: {exc}")
        log.error(msg)
        log.trace(msg)

        raise exc

    saved_comics: list[xkcd_mod.XKCDComic] = []
    for c in comics:
        comic_saved: bool = save_img(comic=c, output_filename=f"{c.num}.png")
        if comic_saved:
            saved_comics.append(c)

    return saved_comics


def pipeline_scrape_missing_comics(
    cache_transport: hishel.CacheTransport = None, request_sleep: int = 5
) -> list[xkcd_mod.XKCDComic] | None:
    assert cache_transport, ValueError("Missing cache transport  for request client")

    log.info(f"Getting current XKCD comic number")
    try:
        current_comic: xkcd_mod.XKCDComic = pipeline_get_current_comic(
            cache_transport=cache_transport
        )
    except Exception as exc:
        msg = Exception(f"Unhandled exception getting current comic. Details: {exc}")
        log.error(msg)
        log.trace(exc)

        raise exc

    # try:
    #     current_comic: xkcd_mod.XKCDComic = _get_current(
    #         cache_transport=cache_transport, force_live_request=True
    #     )
    #     log.debug(f"Current XKCD comic: #{current_comic.num}")
    # except Exception as exc:

    try:
        missing_comic_imgs: list[int] = _list_missing_comic_imgs(
            current_comic_num=current_comic.num
        )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting list of missing comic image numbers. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    if not missing_comic_imgs:
        log.warning(
            f"Did not find any missing comic images. Either an error occurred, or all comic images have been downloaded."
        )

        return None

    if len(missing_comic_imgs) > 1:
        log.debug(f"Scraping [{len(missing_comic_imgs)}] missing comic(s)")
    else:
        log.debug(f"Scraping 1 comic: {missing_comic_imgs[0]}")

    scraped_comics: list[xkcd_mod.XKCDComic] = pipeline_get_multiple_comics(
        cache_transport=cache_transport,
        comic_nums=missing_comic_imgs,
        request_sleep=request_sleep,
    )
    if scraped_comics is None or len(scraped_comics) == 0:
        log.warning(f"No comics were scraped. Have all comic images been downloaded?")

        return

    log.debug(f"Scraped [{len(scraped_comics)}] comic(s)")

    return scraped_comics
