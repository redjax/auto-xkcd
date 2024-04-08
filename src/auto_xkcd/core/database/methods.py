from __future__ import annotations

import sqlalchemy as sa
import sqlalchemy.orm as so

def get_db_uri(
    drivername: str = "sqlite+pysqlite",
    username: str | None = None,
    password: str | None = None,
    host: str | None = None,
    port: int | None = None,
    database: str = "demo.sqlite",
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
    assert drivername is not None, ValueError("drivername cannot be None")
    assert isinstance(drivername, str), TypeError(
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
        assert isinstance(port, int), TypeError(
            f"port must be of type int. Got type: ({type(port)})"
        )
    assert database is not None, ValueError("database cannot be None")
    assert isinstance(database, str), TypeError(
        f"database must be of type str. Got type: ({type(database)})"
    )

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


def get_engine(db_uri: sa.URL = None, echo: bool = False) -> sa.Engine:
    """Get a SQLAlchemy `Engine` instance.

    Params:
        db_uri (sqlalchemy.URL): A database connection string.
        echo (bool): If `True`, engine will echo SQL output to CLI.

    Returns:
        (sqlalchemy.Engine): An initialized SQLAlchemy `Engine`.

    """
    assert db_uri is not None, ValueError("db_uri is not None")
    assert isinstance(db_uri, sa.URL), TypeError(
        f"db_uri must be of type sqlalchemy.URL. Got type: ({type(db_uri)})"
    )

    try:
        engine: sa.Engine = sa.create_engine(url=db_uri, echo=echo)

        return engine
    except Exception as exc:
        msg = Exception(f"Unhandled exception getting database engine. Details: {exc}")

        raise msg


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
    assert base is not None, ValueError("base cannot be None")
    # assert isinstance(base, so.DeclarativeBase), TypeError(
    #     f"base must be of type sqlalchemy.orm.DeclarativeBase. Got type: ({type(base)})"
    # )
    assert engine is not None, ValueError("engine cannot be None")
    assert isinstance(engine, sa.Engine), TypeError(
        f"engine must be of type sqlalchemy.Engine. Got type: ({type(engine)})"
    )

    try:
        base.metadata.create_all(bind=engine)
    except Exception as exc:
        msg = Exception(f"Unhandled exception creating Base metadata. Details: {exc}")
        raise msg
