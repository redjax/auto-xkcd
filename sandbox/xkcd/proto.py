from __future__ import annotations

import random
import typing as t

import core_utils
import db_lib
import db_lib.demo_db
from depends import db_depends
from domain import xkcd as xkcd_domain
import http_lib
from loguru import logger as log
import settings
import setup
import xkcdapi
import xkcdapi.controllers
import xkcdapi.db_client
import xkcdapi.request_client

import sqlalchemy as sa

DEMO_CACHE_TTL: int = 86400

def demo_current_comic():
    xkcd_api_controller: xkcdapi.controllers.XkcdApiController = xkcdapi.controllers.XkcdApiController(cache_ttl=DEMO_CACHE_TTL)
    
    with xkcd_api_controller as api_ctl:
        log.info("Requesting current XKCD comic")
        current_comic = api_ctl.get_current_comic()
        log.debug(f"Current comic: {current_comic}")
        
        current_comic_img = api_ctl.get_comic_img(comic=current_comic)
        log.info(f"Comic image: {current_comic_img}")
        
    return current_comic, current_comic_img


def demo_random_comic(current_comic_num):
    xkcd_api_controller: xkcdapi.controllers.XkcdApiController = xkcdapi.controllers.XkcdApiController(cache_ttl=DEMO_CACHE_TTL)
    
    with xkcd_api_controller as api_ctl:
        while True:
            rand_comic_num: int = random.randint(1, current_comic_num)
            
            if rand_comic_num in xkcd_domain.constants.IGNORE_COMIC_NUMS:
                log.warning(f"Rolled ignored number: {rand_comic_num}. Re-rolling")
                continue
            else:
                break
        
        log.debug(f"Random comic number: {rand_comic_num}")
        
        log.info(f"Requesting comic and image for comic #{rand_comic_num}")
        comic, comic_img = api_ctl.get_comic_and_img(comic_num=rand_comic_num)
        # log.success(f"Comic: {comic}, image: {comic_img}")
        
    return comic, comic_img


def demo_multiple_comics(num_rand_comics: int = 3, current_comic_num: int = None):
    xkcd_api_controller: xkcdapi.controllers.XkcdApiController = xkcdapi.controllers.XkcdApiController(cache_ttl=DEMO_CACHE_TTL)
    
    if not current_comic_num:
        raise ValueError("Missing the current comic number for randomizer max number.")
    
    log.info(f"Requesting {num_rand_comics} random comic(s) & image(s)")
    
    comics: list[xkcd_domain.XkcdComicIn] = []
    comic_imgs: list[xkcd_domain.XkcdComicImgIn] = []
    
    loop: int = 0
    
    while loop < num_rand_comics:
        log.debug(f"[Loop {loop + 1}/{num_rand_comics}]")
        
        rand_comic, rand_img = demo_random_comic(current_comic_num=current_comic_num)
        if rand_comic:
            comics.append(rand_comic)
        else:
            log.warning("Random comic result was None.")
        
        if rand_img:
            comic_imgs.append(rand_img)
        else:
            log.warning("Random comic image result was None.")

        loop += 1
        
    return comics, comic_imgs


def main(db_engine: sa.Engine):
    log.info("XKCD API requests testing.")
    
    ## Get current comic & img
    current_comic, current_comic_img = demo_current_comic()
    if not current_comic:
        log.warning(f"Failed getting current comic")
    else:
        log.success(f"Current comic: {current_comic}")
        
    if not current_comic_img:
        log.warning(f"Failed getting image for current comic")
    else:
        log.success(f"Current comic image: {current_comic_img.num}")
    
    ## Save comic and image at the same time
    db_current_comic, db_current_comic_img = xkcdapi.db_client.save_comic_and_img_to_db(comic=current_comic, comic_img=current_comic_img, engine=db_engine)
    log.debug(f"Saved current comic: {db_current_comic} and curret comic image: {db_current_comic_img}")

    # ## Request random comic & img
    # comic, comic_img = demo_random_comic(current_comic_num=current_comic.num)
    
    # if not comic:
    #     log.warning(f"Failed getting random comic.")
    # else:
    #     log.success(f"Random comic: {comic}")
    
    # ## Save random comic
    # try:
    #     xkcdapi.db_client.save_comic_to_db(comic=comic, engine=db_engine)
    # except Exception as exc:
    #     msg = f"({type(exc)}) Error saving comic to database. Details: {exc}"
    #     log.error(msg)
        
    #     raise exc
    
    # if not comic_img:
    #     log.warning(f"Failed getting random comic image")
    # else:
    #     log.success(f"Random comic image: {comic_img}")
    
    # ## Save random comic img
    # try:
    #     xkcdapi.db_client.save_comic_img_to_db(comic_img=comic_img, engine=db_engine)
    # except Exception as exc:
    #     msg = f"({type(exc)}) Error saving comic image to database. Details: {exc}"
    #     log.error(msg)
        
    #     raise exc
    
    # ## Request multiple random comics & imgs
    # comics, comic_imgs = demo_multiple_comics(num_rand_comics=3, current_comic_num=current_comic.num)
    # comics.append(current_comic)
    # comic_imgs.append(current_comic_img)
    
    # if (not comics) or (isinstance(comics, list) and len(comics) == 0):
    #     log.warning("List of random comics is empty, there may have been an error requesting multiple comics.")
    # else:
    #     log.success(f"Requested [{len(comics)}] random comic(s)")
        
    #     for c in comics:
    #         log.debug(f"Comic: {c}")
        
    # ## Save multiple comics to database
    # try:
    #     db_comics = xkcdapi.db_client.save_multiple_comics_to_db(comics=comics, engine=db_engine)
    # except Exception as exc:
    #     msg = f"({type(exc)}) Error saving [{len(comics)}] comic(s) to database. Details: {exc}"
    #     log.error(msg)
        
    #     raise exc
    
    # log.debug(f"Saved [{len(db_comics)}] comic(s) to the database")
    # log.debug(f"Saved comics: {db_comics}")
        
    # if (not comic_imgs) or (isinstance(comic_imgs, list) and len(comic_imgs) == 0):
    #     log.warning("List of random comic images is empty, there may have been an error requesting multiple comics.")
    # else:
    #     log.success(f"Requested [{len(comic_imgs)}] random comic image(s)")
    
    # ## Save multiple comic images to database
    # try:
    #     db_comic_imgs = xkcdapi.db_client.save_multiple_comic_imgs_to_db(comic_imgs=comic_imgs, engine=db_engine)
    # except Exception as exc:
    #     msg = f"({type(exc)}) Error saving [{len(comics)}] comic image(s) to database. Details: {exc}"
    #     log.error(msg)
        
    #     raise exc
    
    # log.debug(f"Saved [{len(db_comic_imgs)}] comic image(s) to the database")
    # log.debug(f"Saved comic images: {db_comic_imgs}")


if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=settings.LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"), add_file_logger=True, add_error_file_logger=True, colorize=True)
    demo_db_config = db_lib.demo_db.return_demo_db_config()
    db_uri = db_depends.get_db_uri(**demo_db_config)
    db_engine = db_depends.get_db_engine(db_uri)
    setup.setup_database(engine=db_engine)
    
    main(db_engine=db_engine)
