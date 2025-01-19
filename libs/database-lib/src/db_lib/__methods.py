from __future__ import annotations

import logging
import typing as t

log = logging.getLogger(__name__)

from settings import DB_SETTINGS
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as so
import sqlalchemy.sql as sa_sql

def get_db_uri(
    drivername: str,
    username: str | None,
    password: str | None,
    host: str | None,
    port: int | None,
    database: str,
) -> sa.URL:
    """Construct a SQLAlchemy `URL` for a database connection.

    Params:
        drivername (str): The SQLAlchemy drivername value, i.e. `sqlite+pysqlite`.
        username (str|None): The username for database auth.
        password (str|None): The password for database auth.
        host (str|None): The database server host address.
        port (int|None): The database server port.
        database (str): The database to connect to. For SQLite, use a file path, i.e. `path/to/app.sqlite`.

    """
    if drivername is None:
        raise ValueError("drivername cannot be None")
    if not isinstance(drivername, str):
        raise TypeError(
            f"drivername must be of type str. Got type: ({type(drivername)})"
        )
    if username is not None:
        assert isinstance(username, str), TypeError(
            f"username must be of type str. Got type: ({type(username)})"
        )
    if password is not None:
        assert isinstance(password, str), TypeError(
            f"password must be of type str. Got type: ({type(password)})"
        )
    if host is not None:
        assert isinstance(host, str), TypeError(
            f"host must be of type str. Got type: ({type(host)})"
        )
    if port is not None:
        if not isinstance(port, int):
            if isinstance(port, str) and port == "":
                port = None
            else:
                try:
                    port: int = int(port)
                except Exception as exc:
                    msg = f"({type(exc)}) 'port' must be of type int. Got type: ({type(port)}), and failed converting to int."
                    log.error(msg)

                    raise exc

    if database is None:
        raise ValueError("database cannot be None")
    if not isinstance(database, str):
        raise TypeError(f"database must be of type str. Got type: ({type(database)})")

    try:
        db_uri: sa.URL = sa.URL.create(
            drivername=drivername,
            username=username,
            password=password,
            host=host,
            port=port,
            database=database,
        )

        return db_uri
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception creating SQLAlchemy URL from inputs. Details: {exc}"
        )

        raise msg


def get_engine(
    pool: sa.Pool | None = None,
    url: sa.URL = None,
    logging_name: str | None = None,
    execution_options: dict | None = None,
    hide_parameters: bool = False,
    echo: bool = DB_SETTINGS.get("DB_ECHO", default=False),
    query_cache_size: int = 500,
) -> sa.Engine:
    engine = sa.create_engine(
        pool=pool,
        logging_name=logging_name,
        execution_options=execution_options,
        url=url,
        echo=echo,
        hide_parameters=hide_parameters,
        query_cache_size=query_cache_size,
    )

    return engine


def get_session_pool(engine: sa.Engine = None) -> so.sessionmaker[so.Session]:
    """Return a SQLAlchemy session pool.

    Params:
        engine (sqlalchemy.Engine): A SQLAlchemy `Engine` to use for database connections.

    Returns:
        (sqlalchemy.orm.sessionmaker): A SQLAlchemy `Session` pool for database connections.

    """
    assert engine is not None, ValueError("engine cannot be None")
    assert isinstance(engine, sa.Engine), TypeError(
        f"engine must be of type sqlalchemy.Engine. Got type: ({type(engine)})"
    )

    session_pool: so.sessionmaker[so.Session] = so.sessionmaker(bind=engine)

    return session_pool


def create_base_metadata(
    base: so.DeclarativeBase = None, engine: sa.Engine = None
) -> None:
    """Create a SQLAlchemy base object's table metadata.

    Params:
        base (sqlalchemy.orm.DeclarativeBase): A SQLAlchemy `DeclarativeBase` object to use for creating metadata.
    """
    if base is None:
        raise ValueError("base cannot be None")
    if engine is None:
        raise ValueError("engine cannot be None")
    if not isinstance(engine, sa.Engine):
        raise TypeError(
            f"engine must be of type sqlalchemy.Engine. Got type: ({type(engine)})"
        )

    try:
        base.metadata.create_all(bind=engine)
    except Exception as exc:
        msg = Exception(
            f"({type(exc)}) Unhandled exception creating Base metadata. Details: {exc}"
        )
        raise msg


def count_table_rows(table: str, engine: sa.Engine, echo: bool = False) -> int:
    """Count the number of rows in a table.
    
    Params:
        table (str): The name of the table to count rows in.
        engine (sqlalchemy.Engine): A SQLAlchemy `Engine` to use for database connections.
    """
    log.info(f"Counting rows in table: {table}")
    
    session_pool = get_session_pool(engine=engine)
    
    ## Count number of rows in given table name
    with session_pool() as session:
        if not sa.inspect(engine).has_table(table):
            log.error(f"Table '{table}' does not exist.")
            return
        
        query = sa_sql.text(f"SELECT COUNT(*) FROM {table}")
        try:
            count = session.execute(query).scalar()
        except Exception as exc:
            msg= f"({type(exc)}) Error counting rows in table '{table}'. Details: {exc}"
            log.error(msg)
            
            raise exc
        except sa_exc.SQLAlchemyError as exc:
            log.error(f"Error querying table '{table}': {exc}")
        
        log.info(f"[{count}] row(s) in table '{table}'.")
        
        return count
    

def show_table_names(engine: sa.Engine, echo: bool = False) -> list[str]:
    """List all table names in the database.
    
    Params:
        engine (sqlalchemy.Engine): A SQLAlchemy `Engine` to use for database connections.
        echo (bool): Echo the table names to the console.
    """
    log.info("Showing database tables")
    
    inspector = sa.inspect(engine)
    tables = inspector.get_table_names()
    
    if tables:
        log.debug(f"Tables in the database: {tables}")
        return tables
    else:
        log.warning("No tables found in the database.")
        return
