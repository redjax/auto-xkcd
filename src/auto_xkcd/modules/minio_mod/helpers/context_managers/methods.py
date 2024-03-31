import typing as t
from pathlib import Path
from contextlib import contextmanager

from core import MinioSettings
from .classes import MinioController

import minio
from minio.error import (
    S3Error,
    ServerError,
    MinioException,
    MinioAdminException,
    InvalidResponseError,
)

from loguru import logger as log


@contextmanager
def get_minio_controller(
    minio_settings: MinioSettings = None,
) -> t.Generator[MinioController, t.Any, None]:
    assert minio_settings, ValueError("Missing MinioSettings object.")
    assert isinstance(minio_settings, MinioSettings), TypeError(
        f"minio_settings must be of type MinioSettings. Got type: ({type(minio_settings)})"
    )

    try:
        with MinioController(
            endpoint=minio_settings.endpoint,
            secure=minio_settings.secure,
            access_key=minio_settings.access_key,
            secret_key=minio_settings.access_secret,
        ) as _controller:
            yield _controller

    except S3Error as s3_err:
        msg = Exception(f"S3Error getting MinioController. Details: {s3_err}")
        log.error(msg)

        raise msg

    except Exception as exc:
        msg = Exception(f"Unhandled exception yielding MinioController. Details: {exc}")
        log.error(msg)

        raise msg
