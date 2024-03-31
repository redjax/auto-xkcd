from __future__ import annotations

from contextlib import contextmanager
import typing as t

from core import _exc, database
from core.config import AppSettings, DBSettings, MinioSettings, TelegramSettings
from core.request_client import CACHE_STORAGE, CACHE_TRANSPORT
from dynaconf import Dynaconf
import hishel
import httpx
from loguru import logger as log
import minio
import sqlalchemy as sa
import sqlalchemy.orm as so

DYNACONF_SETTINGS: Dynaconf = Dynaconf(
    environments=True,
    envvar_prefix="DYNACONF",
    settings_files=["settings.toml", ".secrets.toml"],
)
DYNACONF_DB_SETTINGS: Dynaconf = Dynaconf()
DYNACONF_MINIO_SETTINGS: Dynaconf = Dynaconf(
    environments=True,
    envvar_prefix="MINIO",
    settings_files=["minio/settings.toml", "minio/.secrets.toml"],
)

settings: AppSettings = AppSettings(
    env=DYNACONF_SETTINGS.ENV,
    container_env=DYNACONF_SETTINGS.CONTAINER_ENV,
    log_level=DYNACONF_SETTINGS.LOG_LEVEL,
    logs_dir=DYNACONF_SETTINGS.LOGS_DIR,
)
## Uncomment if you're configuring a database for the app
db_settings: DBSettings = DBSettings()
telegram_settings: TelegramSettings = TelegramSettings()
minio_settings: MinioSettings = MinioSettings(
    address=DYNACONF_MINIO_SETTINGS.MINIO_ADDRESS,
    port=DYNACONF_MINIO_SETTINGS.MINIO_PORT,
    secure=DYNACONF_MINIO_SETTINGS.MINIO_HTTPS,
    username=DYNACONF_MINIO_SETTINGS.MINIO_USERNAME,
    password=DYNACONF_MINIO_SETTINGS.MINIO_PASSWORD,
    access_key=DYNACONF_MINIO_SETTINGS.MINIO_ACCESS_KEY,
    access_secret=DYNACONF_MINIO_SETTINGS.MINIO_ACCESS_SECRET,
)

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
