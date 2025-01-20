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

def main(db_engine: sa.Engine):
    log.info("Test script to crawl XKCD API")


if __name__ == "__main__":
    setup.setup_loguru_logging(log_level=settings.LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO"), add_file_logger=True, add_error_file_logger=True, colorize=True)
    demo_db_config = db_lib.demo_db.return_demo_db_config()
    db_uri = db_depends.get_db_uri(**demo_db_config)
    db_engine = db_depends.get_db_engine(db_uri)
    setup.setup_database(engine=db_engine)
    
    main(db_engine=db_engine)
