"""Importable dependencies for the app.

Includes initialized `Dynaconf` settings objects, initialized SQLAlchemy variables,
and methods/context managers for yielding objects like a database connection.
"""

from __future__ import annotations

from contextlib import contextmanager
import typing as t

from core import database, request_client
from core.config import AppSettings, DBSettings, MinioSettings, TelegramSettings
from core.config import settings, db_settings, telegram_settings
from dynaconf import Dynaconf
import hishel
import httpx
from loguru import logger as log
import sqlalchemy as sa
import sqlalchemy.orm as so


DB_URI: sa.URL = db_settings.get_db_uri()
ENGINE: sa.Engine = database.get_engine(db_uri=DB_URI, echo=db_settings.echo)
SESSION_POOL: so.sessionmaker[so.Session] = database.get_session_pool(engine=ENGINE)

CACHE_TRANSPORT: hishel.CacheTransport = request_client.get_cache_transport(retries=3)


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


# @contextmanager
# def get_minio_client(
#     minio_settings: MinioSettings = minio_settings,
# ) -> t.Generator[minio.Minio, t.Any, None]:
#     assert minio_settings, ValueError("Missing MinioSettings object")
#     assert isinstance(minio_settings, MinioSettings), TypeError(
#         f"minio_settings must be a MinioSettings object. Got type: ({type(minio_settings)})"
#     )

#     try:
#         _client: minio.Minio = minio.Minio(
#             endpoint=minio_settings.endpoint,
#             secure=minio_settings.secure,
#             access_key=minio_settings.access_key,
#             secret_key=minio_settings.access_secret,
#         )

#         yield _client
#     except _exc.S3Error as s3_err:
#         msg = Exception(f"S3Error during minio connection. Details: {s3_err}")
#         log.error(msg)

#         raise s3_err
#     except _exc.MaxRetryError as max_retry_err:
#         msg = Exception(
#             f"Max retries exceeded attempting connection to endpoint: {minio_settings.endpoint}. Details: {max_retry_err}"
#         )
#         log.error(msg)

#         raise max_retry_err
#     except minio.ServerError as minio_srv_err:
#         msg = f"Minio ServerError occurred. Details: {minio_srv_err}"
#         log.error(msg)

#         raise minio_srv_err
#     except minio.S3Error as minio_s3_err:
#         msg = f"Minio S3Error occurred. Details: {minio_s3_err}"
#         log.error(msg)

#         raise minio_s3_err
#     except Exception as exc:
#         msg = Exception(f"Unhandled exception yielding Minio client. Details: {exc}")
#         log.error(msg)

#         raise exc
