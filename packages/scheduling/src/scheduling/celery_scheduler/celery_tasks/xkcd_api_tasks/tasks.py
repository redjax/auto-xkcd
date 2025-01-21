from __future__ import annotations

from pathlib import Path
import time
import typing as t

from celery import current_app
from celery.result import AsyncResult
import db_lib
import depends
from domain import xkcd as xkcd_domain
import httpx
from loguru import logger as log
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as so
import xkcdapi
import xkcdapi.controllers
import xkcdapi.db_client
import xkcdapi.request_client

@current_app.task(name="request_current_comic")
def task_current_comic() -> dict:
    log.info("Running Celery task to request current XKCD comic")
    
    xkcd_api_controller: xkcdapi.controllers.XkcdApiController = xkcdapi.controllers.XkcdApiController()
    
    try:
        current_comic: xkcd_domain.XkcdComicIn = xkcd_api_controller.get_current_comic()
        if not current_comic:
            log.warning("current_comic is None, indicating an error requesting the comic from the XKCD API.")
            return
        
        log.success("Retrieved current XKCD comic from the XKCD API.")
        
        return current_comic.model_dump()
    except Exception as exc:
        msg = f"({type(exc)}) Error requesting current XKCD comic. Details: {exc}"
        log.error(msg)
        
        raise exc


@current_app.task(name="request_and_save_current_comic")
def task_save_current_comic(engine: sa.Engine | None = None) -> t.Tuple[dict | None, dict | None]:
    log.info("Running Celery task to request current XKCD comic & image, and save both to the database.")
    
    if not engine:
        log.warning("No SQLAlchemy Engine object detected. Initializing Engine with app's database settings.")
        engine: sa.Engine = depends.db_depends.get_db_engine()
    
    xkcd_api_controller: xkcdapi.controllers.XkcdApiController = xkcdapi.controllers.XkcdApiController()
    session_pool: so.sessionmaker[so.Session] = depends.db_depends.get_session_pool(engine=engine)
    
    with xkcd_api_controller as api_ctl:
        log.info("Requesting current XKCD comic")
        current_comic: xkcd_domain.XkcdComicIn = api_ctl.get_current_comic()
        log.info("Requesting current XKCD comic image")
        current_comic_img: xkcd_domain.XkcdComicImgIn = api_ctl.get_comic_img(comic=current_comic)
    
    log.info("Saving XKCD comic and image to database")
    db_current_comic, db_current_comic_img = xkcdapi.db_client.save_comic_and_img_to_db(comic=current_comic, comic_img=current_comic_img, session_pool=session_pool)
    
    if not db_current_comic:
        log.warning("db_current_comic is None, indicating an issue saving the current comic to the database. Returning None for the comic object")
        comic_out_dict = None
    else:
        comic_out_dict = db_current_comic.model_dump()
    
    if not db_current_comic_img:
        log.warning("db_current_comic_img is None, indicating an issue saving the current comic's image to the database. Returning None for the comic image object")
        comic_img_out_dict = None
    else:
        comic_img_out_dict = db_current_comic_img.model_dump()
    
    return comic_out_dict, comic_img_out_dict