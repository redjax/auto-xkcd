"""A temporary testing ground for new features. New pipelines are created from the starting point here. This file will eventually be removed."""

from __future__ import annotations

from pathlib import Path
import typing as t

from _setup import base_app_setup
from core import (
    COMIC_IMG_DIR,
    CURRENT_XKCD_URL,
    SERIALIZE_COMIC_OBJECTS_DIR,
    SERIALIZE_COMIC_RESPONSES_DIR,
    XKCD_URL_BASE,
    XKCD_URL_POSTFIX,
    request_client,
)
from core.dependencies import settings
from domain.xkcd.comic import XKCDComic
from helpers.validators import validate_hishel_cachetransport
import hishel
import httpx
from loguru import logger as log
from modules import requests_prefab, xkcd_mod, data_mod
import msgpack
from packages import xkcd_comic
from pipelines import comic_pipelines
from utils import serialize_utils

import pandas as pd
import ibis


def test_deserialize_to_df():
    files: list[Path] = []
    deser_dicts: list[dict] = []
    dfs: list[pd.DataFrame] = []

    log.info(f"Scanning path: '{SERIALIZE_COMIC_OBJECTS_DIR}'")
    for f in SERIALIZE_COMIC_OBJECTS_DIR.glob("**/*.msgpack"):
        files.append(f)

        with open(f, "rb") as fp:
            data = fp.read()
            _deser: dict = msgpack.unpackb(data)
            deser_dicts.append(_deser)
            _df: pd.DataFrame = pd.DataFrame([_deser])
            dfs.append(_df)

    _sample = deser_dicts[0]
    # log.debug(f"Example dict ({type(_sample)}): {_sample}")
    _sampled_comic: XKCDComic = XKCDComic.model_validate(_sample)
    log.debug(f"Sampled comic: {_sampled_comic}")

    log.debug(f"Joining [{len(dfs)}] DataFrame(s)")
    df: pd.DataFrame = pd.concat(dfs)
    log.debug(f"DataFrame:\n{df.head(5)}")

    pq_file = Path("test_pq.parquet")
    log.info(f"Saving DataFrame to '{pq_file}'")
    try:
        df.to_parquet(pq_file, engine="fastparquet")
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception saving DataFrame to file '{pq_file}'. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc


def main(cache_transport: hishel.CacheTransport = None):
    cache_transport = validate_hishel_cachetransport(cache_transport=cache_transport)

    # comic: XKCDComic = xkcd_comic.get_current_comic(
    #     cache_transport=cache_transport, overwrite_serialized_comic=True
    # )
    # log.debug(f"Comic: {comic}")

    # deserialized_comic: XKCDComic | None = xkcd_mod.load_serialized_comic(
    #     comic_num=comic.num
    # )
    # log.debug(f"Deserialized comic ({type(deserialized_comic)}): {deserialized_comic}")

    # comic: XKCDComic = xkcd_comic.get_single_comic(
    #     cache_transport=cache_transport, overwrite_serialized_comic=True, comic_num=42
    # )
    # log.debug(f"Comic #42: {comic}")

    # comic: XKCDComic = xkcd_comic.get_single_comic(
    #     cache_transport=cache_transport, overwrite_serialized_comic=True, comic_num=42
    # )
    # log.debug(f"Comic #{comic.num}: {comic}")

    # comics: list[XKCDComic] = comic_pipelines.pipeline_multiple_comics(
    #     cache_transport=cache_transport,
    #     comic_nums=[1, 24, 86, 92, 320, 500, 555, 615, 645, 720, 732],
    #     request_sleep=5,
    # )

    # scraped_comics: list[XKCDComic] | None = xkcd_comic.scrape_missing_comics(
    #     cache_transport=cache_transport, request_sleep=5
    # )


if __name__ == "__main__":
    base_app_setup(settings=settings)
    log.info(f"[TEST][env:{settings.env}|container:{settings.container_env}] App Start")

    CACHE_TRANSPORT: hishel.CacheTransport = request_client.get_cache_transport()

    # current_comic: XKCDComic = comic_pipelines.pipeline_current_comic(
    #     cache_transport=CACHE_TRANSPORT
    # )
    # log.debug(f"Current comic ({type(current_comic)}): {current_comic}")

    # main(cache_transport=CACHE_TRANSPORT)

    # test_deserialize_to_df()
    all_requested_comics_df: pd.DataFrame = data_mod.deserialize_comics_to_df(
        scan_path=SERIALIZE_COMIC_OBJECTS_DIR
    )
    log.debug(f"DataFrame shape: ({all_requested_comics_df.shape[0]})")
    log.debug(f"Columns: {all_requested_comics_df.columns}")
    log.debug(f"First 5: {all_requested_comics_df.head(5)}")
