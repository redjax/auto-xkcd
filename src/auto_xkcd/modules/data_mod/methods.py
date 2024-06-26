from __future__ import annotations

from pathlib import Path
import typing as t

from core.constants import PQ_ENGINE
from core.paths import COMICS_PQ_FILE
from domain.xkcd import XKCDComic
from loguru import logger as log
import msgpack
import pandas as pd

def deserialize_comics_to_df(
    scan_path: t.Union[str, Path] = None,
    # output_file: t.Union[str, Path] = None,
    filetype_filter: str = ".msgpack",
) -> pd.DataFrame:
    files: list[Path] = []
    deser_dicts: list[dict] = []
    dfs: list[pd.DataFrame] = []

    log.info(f"Scanning path: '{scan_path}'")
    for f in scan_path.glob(f"**/*{filetype_filter}"):
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

    log.info(f"Saving DataFrame to '{COMICS_PQ_FILE}'")
    try:
        df.to_parquet(COMICS_PQ_FILE, engine="fastparquet")
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception saving DataFrame to file '{COMICS_PQ_FILE}'. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc

    return df


def load_pq_to_df(
    comics_pq_file: t.Union[str, Path] = None, pq_engine: str = PQ_ENGINE
) -> pd.DataFrame:
    assert comics_pq_file, ValueError("Missing comics_pq_file path")
    comics_pq_file: Path = Path(f"{comics_pq_file}")
    if "~" in f"{comics_pq_file}":
        comics_pq_file = comics_pq_file.expanduser()

    try:
        _df: pd.DataFrame = pd.read_parquet(path=comics_pq_file, engine=pq_engine)
        return _df
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception loading parquet file '{comics_pq_file}' into Pandas DataFrame. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc
