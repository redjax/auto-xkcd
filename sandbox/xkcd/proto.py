from loguru import logger as log

import typing as t

import db_lib
import db_lib.demo_db
import http_lib
from depends import db_depends
import xkcdapi
import settings
import setup
import core_utils
import xkcdapi.request_client


if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=settings.LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"))
    demo_db_config = db_lib.demo_db.return_demo_db_config()
    db_uri = db_depends.get_db_uri(**demo_db_config)
    db_engine = db_depends.get_db_engine(db_uri)
    setup.setup_database(engine=db_engine)
    
    log.info("XKCD API requests testing.")
    current_comic_response = xkcdapi.request_client.request_current_xkcd_comic()
