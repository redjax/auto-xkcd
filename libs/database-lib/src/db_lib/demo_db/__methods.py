from __future__ import annotations

from db_lib.__methods import get_db_uri, get_engine, get_session_pool

from .constants import DEMO_DB_CONFIG

from loguru import logger as log
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as so

def return_demo_db_config(
    drivername: str = "sqlite+pysqlite",
    username: str | None = None,
    password: str | None = None,
    host: str | None = None,
    port: int | None = None,
    database: str = ".db/demo.sqlite3",
) -> dict:
    db_config: dict = {
        "drivername": drivername or "sqlite+pysqlite",
        "username": username,
        "password": password,
        "host": host,
        "port": port,
        "database": database or ".db/demo.sqlite3",
    }
    
    return db_config


def return_demo_engine(db_conf: dict = DEMO_DB_CONFIG, echo: bool = False) -> sa.Engine:
    db_uri = get_db_uri(**db_conf)
    engine = get_engine(url=db_uri, echo=echo)

    return engine
