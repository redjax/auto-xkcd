from domain.xkcd.comic.schemas import XKCDComic
from entrypoints import pipeline_entrypoints
from _setup import base_app_setup
from core.dependencies import settings, db_settings
from core import request_client, database, paths
from core.constants import PQ_ENGINE
from modules import xkcd_mod, data_mod


from loguru import logger as log
import hishel
import httpx


def main(cache_transport: hishel.CacheTransport = None, pq_engine: str = PQ_ENGINE):
    current_comic: XKCDComic = (
        pipeline_entrypoints.start_current_comic_pipeline.run_pipeline(
            cache_transport=CACHE_TRANSPORT, overwrite_serialized_comic=True
        )
    )
    log.debug(f"Current comic: {current_comic}")

    pipeline_entrypoints.start_save_serialized_comics_to_db_pipeline.run_pipeline(
        db_settings=db_settings,
        sqla_base=database.Base,
        serialized_comics_dir=paths.SERIALIZE_COMIC_OBJECTS_DIR,
        db_comics_tbl_name="xkcd_comic",
        if_exists_strategy="replace",
        save_parquet=True,
        pq_output_file=paths.COMICS_PQ_FILE,
        pq_engine=pq_engine,
    )


if __name__ == "__main__":
    base_app_setup()

    CACHE_TRANSPORT = request_client.get_cache_transport()

    main(cache_transport=CACHE_TRANSPORT)
