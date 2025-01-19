from __future__ import annotations

import logging
import typing as t

log = logging.getLogger(__name__)

import db_lib as db
from settings import DB_SETTINGS
import sqlalchemy as sa
import sqlalchemy.orm as so

def get_db_uri(
    drivername: str = DB_SETTINGS.get("DB_DRIVERNAME", default="sqlite+pysqlite"),
    username: str | None = DB_SETTINGS.get("DB_USERNAME", default=None),
    password: str | None = DB_SETTINGS.get("DB_PASSWORD", default=None),
    host: str | None = DB_SETTINGS.get("DB_HOST", default=None),
    port: int | None = DB_SETTINGS.get("DB_PORT", default=None),
    database: str = DB_SETTINGS.get("DB_DATABASE", default="demo.sqlite"),
    as_str: bool = False,
) -> sa.URL:
    """Construct a SQLAlchemy `URL` for a database connection.
    
    Params:
        drivername (str): The SQLAlchemy drivername value, i.e. `sqlite+pysqlite`.
        username (str|None): The username for database auth.
        password (str|None): The password for database auth.
        host (str|None): The database server host address.
        port (int|None): The database server port.
        database (str): The database to connect to. For SQLite, use a file path, i.e. `path/to/app.sqlite`.
        as_str (bool): Return the SQLAlchemy `URL` as a string.
        
    Returns:
        (sa.URL): A SQLAlchemy `URL`

    """
    if DB_SETTINGS.get("DB_TYPE") == "sqlite":
        db_uri: sa.URL = db.get_db_uri(drivername=drivername, database=database, username=None, password=None, host=None, port=None)
        
        if as_str:
            return str(db_uri)
        else:
            return db_uri

    db_uri: sa.URL = db.get_db_uri(
        drivername=drivername,
        username=username,
        password=password,
        host=host,
        port=port,
        database=database,
    )

    if as_str:
        return str(db_uri)
    else:
        return db_uri


def get_db_engine(db_uri: sa.URL = get_db_uri(), echo: bool = False) -> sa.Engine:
    """Construct a SQLAlchemy `Engine` for a database connection.
    
    Params:
        db_uri (sa.URL): A SQLAlchemy `URL` for a database connection.
        echo (bool): Echo SQL statements to the console.
        
    Returns:
        (sa.Engine): A SQLAlchemy `Engine`

    """
    engine: sa.Engine = db.get_engine(url=db_uri, echo=echo)

    return engine


def get_session_pool(
    engine: sa.Engine = get_db_engine(),
) -> so.sessionmaker[so.Session]:
    """Construct a SQLAlchemy `Session` pool for a database connection.
    
    Params:
        engine (sa.Engine): A SQLAlchemy `Engine` for a database connection.
        
    Returns:
        (so.sessionmaker[so.Session]): A SQLAlchemy `Session` pool

    """
    session: so.sessionmaker[so.Session] = db.get_session_pool(engine=engine)

    return session