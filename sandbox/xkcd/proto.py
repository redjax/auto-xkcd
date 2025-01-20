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
import xkcdapi.request_client

def demo_current_comic():
    xkcd_api_controller: xkcdapi.controllers.XkcdApiController = xkcdapi.controllers.XkcdApiController(cache_ttl=86400)
    
    with xkcd_api_controller as api_ctl:
        log.info("Requesting current XKCD comic")
        current_comic = api_ctl.get_current_comic()
        log.debug(f"Current comic: {current_comic}")
        
        current_comic_img = api_ctl.get_comic_img(comic=current_comic)
        log.info(f"Comic image: {current_comic_img}")
        
    return current_comic, current_comic_img


def demo_random_comic(current_comic_num):
    xkcd_api_controller: xkcdapi.controllers.XkcdApiController = xkcdapi.controllers.XkcdApiController(cache_ttl=86400)
    
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


def main():
    log.info("XKCD API requests testing.")
    
    current_comic, current_comic_img = demo_current_comic()
    if not current_comic:
        log.warning(f"Failed getting current comit")
    else:
        log.success(f"Current comic: {current_comic}")
    
    if not current_comic_img:
        log.warning(f"Failed getting image for current comic")
    else:
        log.success(f"Current comic image: {current_comic_img}")

    comic, comic_img = demo_random_comic(current_comic_num=current_comic.num)
    
    if not comic:
        log.warning(f"Failed getting random comic.")
    else:
        log.success(f"Random comic: {comic}")
    
    if not comic_img:
        log.warning(f"Failed getting random comic image")
    else:
        log.success(f"Random comic image: {comic_img}")


if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=settings.LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"), colorize=True)
    demo_db_config = db_lib.demo_db.return_demo_db_config()
    db_uri = db_depends.get_db_uri(**demo_db_config)
    db_engine = db_depends.get_db_engine(db_uri)
    setup.setup_database(engine=db_engine)
    
    main()
