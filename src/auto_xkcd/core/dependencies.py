from __future__ import annotations

from contextlib import contextmanager
import typing as t

from core import DBSettings, database, db_settings
from core.request_client import CACHE_STORAGE, CACHE_TRANSPORT
import hishel
import httpx
import sqlalchemy as sa
import sqlalchemy.orm as so

DB_URI: sa.URL = db_settings.get_db_uri()
ENGINE: sa.Engine = database.get_engine(db_uri=DB_URI, echo=db_settings.echo)
SESSION_POOL: so.sessionmaker[so.Session] = database.get_session_pool(engine=ENGINE)


@contextmanager
def get_db() -> t.Generator[so.Session, t.Any, None]:
    """Dependency to yield a SQLAlchemy Session pool.

    Usage:

        ```py title="get_db() dependency usage" linenums="1"

        from core.dependencies import get_db

        with get_db() as session:
            repo = someRepoClass(session)

            all = repo.get_all()
        ```
    """
    db: so.Session = SESSION_POOL()

    try:
        yield db
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception yielding database session. Details: {exc}"
        )

        raise msg
    finally:
        db.close()
