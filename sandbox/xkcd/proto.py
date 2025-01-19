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

def main():
    log.info("XKCD API requests testing.")
    
    xkcd_api_controller: xkcdapi.controllers.XkcdApiController = xkcdapi.controllers.XkcdApiController(use_cache=True, force_cache=True)
    
    log.info("Requesting current XKCD comic")
    current_comic = xkcd_api_controller.get_current_comic()
    log.info(f'Current comic: {current_comic}')
    
    current_comic_img = xkcd_api_controller.get_comic_img(comic=current_comic)
    log.info(f"Comic image: {current_comic_img}")
    
    while True:
        # rand_comic_num: int = random.randint(1, current_comic.num)
        rand_comic_num: int = random.randint(403, 405)
        
        if rand_comic_num in xkcd_domain.constants.IGNORE_COMIC_NUMS:
            log.warning(f"Rolled ignored number: {rand_comic_num}. Re-rolling")
            continue
        else:
            break
        
    log.debug(f"Random comic number: {rand_comic_num}")


if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=settings.LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"))
    demo_db_config = db_lib.demo_db.return_demo_db_config()
    db_uri = db_depends.get_db_uri(**demo_db_config)
    db_engine = db_depends.get_db_engine(db_uri)
    setup.setup_database(engine=db_engine)
    
    main()
