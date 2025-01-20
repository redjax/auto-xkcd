from loguru import logger as log

import typing as t

import http_lib
from core_utils import time_utils
import setup
import settings
import db_lib
from depends import db_depends
import xkcdapi
from domain import xkcd as xkcd_domain
import xkcdapi.db_client
import xkcdapi.request_client
import xkcdapi.controllers

import httpx
import sqlalchemy as sa
import sqlalchemy.orm as so

def request_and_update_current_comic_metadata(cache_ttl: int = 900, session_pool: so.sessionmaker[so.Session] | None = None, db_engine: sa.Engine | None = None):
    log.info("Updating current XKCD comic metadata in database.")
    
    xkcd_api_controller: xkcdapi.controllers.XkcdApiController = xkcdapi.controllers.XkcdApiController(cache_ttl=cache_ttl)
    
    with xkcd_api_controller as api_ctl:
        log.info("Requesting current XKCD comic")
        current_comic = api_ctl.get_current_comic()
        log.debug(f"Current comic: {current_comic}")
        
        current_comic_img = api_ctl.get_comic_img(comic=current_comic)
        log.info(f"Comic image: {current_comic_img}")
    
    ## Set timestamp immediately after request
    ts = time_utils.get_ts(as_str=False)
    
    if not current_comic:
        raise ValueError("Error requesting the current XKCD comic from XKCD's web API.")

    ## Save the current comic to the database, if it does not exist
    db_current_comic: xkcd_domain.XkcdComicModel = xkcdapi.db_client.save_comic_to_db(comic=current_comic)
    if not db_current_comic:
        log.warning("HTTP request for current comic succeeded, but database model is empty, indicating a failure saving the comic data to the database.")

    ## Save the current comic image to the database, if it does not exist
    if not current_comic_img:
        log.warning(f"Current comic requested successfully, but an error occurred requesting the image for comic #{current_comic.num}")
        db_current_comic_img = None
    else:
        db_current_comic_img: xkcd_domain.XkcdComicImageModel = xkcdapi.db_client.save_comic_img_to_db(comic_img=current_comic_img)
    
    if not db_current_comic_img:
        log.warning("HTTP request for current comic image succeeded, but database model is empty, indicating a failure saving the comic image data to the database.")
        
    ## Create current comic metadata schema object
    current_meta: xkcd_domain.XkcdCurrentComicMetadataIn = xkcd_domain.XkcdCurrentComicMetadataIn(num=current_comic.num, last_updated=ts)
    log.debug(f"Created metadata object: {current_meta}")
    
    ## Save or update current comic metadata
    db_current_meta: xkcd_domain.XkcdCurrentComicMetadataOut = xkcdapi.db_client.update_db_current_comic_metadata(comic_metadata=current_meta)
    
    return db_current_meta


def get_existing_current_comic_metadata(session_pool: so.sessionmaker[so.Session] | None = None, db_engine: sa.Engine | None = None):
    db_current_metadata = xkcdapi.db_client.get_current_comic_metadata_from_db(session_pool=session_pool, engine=db_engine)
    log.info(f"Retrieved current comic metadata from database: {db_current_metadata}")
    
    return db_current_metadata


def main(cache_ttl: int = 900, session_pool: so.sessionmaker[so.Session] | None = None, db_engine: sa.Engine | None = None):
    current_comic_metadata: xkcd_domain.XkcdCurrentComicMetadataOut = request_and_update_current_comic_metadata(cache_ttl=cache_ttl, session_pool=session_pool, db_engine=db_engine)
    log.info(f"Updated current comic metadata: {current_comic_metadata}")


if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=settings.LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"), colorize=True)
    setup.setup_database()
    
    main()
    # get_existing_current_comic_metadata()
