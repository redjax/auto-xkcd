import typing as t

from functools import lru_cache
import json
import time

from core import request_client
from core.config import db_settings, settings
from core.dependencies import get_db
from modules import xkcd_mod
from packages import xkcd_comic
from domain.xkcd import comic
from modules.celery_mod.celeryapp import CELERY_APP
from modules.celery_mod.celery_config import celery_settings
from loguru import logger as log


## Get existing comics from database, cache in memory after first execution
@lru_cache
def existing_comics() -> list[comic.XKCDComicModel]:
    with get_db() as session:
        repo = comic.XKCDComicRepository(session=session)

        all_db_comics: list[comic.XKCDComicModel] = repo.get_all()

        log.info(f"Retrieved [{len(all_db_comics)}] from database.")
        if all_db_comics:
            log.debug(
                f"Sample comic: {comic.XKCDComicOut.model_validate(all_db_comics[0].__dict__)}"
            )
    return all_db_comics
