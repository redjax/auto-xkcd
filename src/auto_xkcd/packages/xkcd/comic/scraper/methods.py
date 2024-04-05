import typing as t

from modules import xkcd_mod
from packages.xkcd.comic.methods import get_multiple_comics, request_comic


from loguru import logger as log
import httpx
import hishel


def start_scrape(cache_transport: hishel.CacheTransport = None):
    log.info(f"Scraping missing comics.")
