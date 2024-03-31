from pathlib import Path

from core import (
    MinioSettings,
    minio_settings,
    settings,
    AppSettings,
    db_settings,
    DBSettings,
    _exc,
)
from core import database, get_db, get_minio_client

from loguru import logger as log
from red_utils.ext.loguru_utils import init_logger, sinks
import minio
from minio.datatypes import Bucket

import httpx


if __name__ == "__main__":
    init_logger(sinks=[sinks.LoguruSinkStdErr(level=settings.log_level).as_dict()])

    log.info(f"[env:{settings.env}|container:{settings.container_env}] Start auto-xkcd")

    log.debug(f"Settings: {settings}")
    log.debug(f"DB settings: {db_settings}")
    log.debug(f"Minio settings: {minio_settings}")

    log.info("Attempting to upload testfile.txt")
    src_file = "testfile.txt"
    bucket = "auto-xkcd"
    dst_file = "testfile.txt"

    with get_minio_client() as minio_client:
        _buckets: list[Bucket] = minio_client.list_buckets()
        log.debug(f"Buckets: {_buckets}")

        ## Create bucket if it doesn't exist
        found: bool = minio_client.bucket_exists(bucket)
        if not found:
            try:
                minio_client.make_bucket(bucket)
                log.success(f"Bucket created: {bucket}")
            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception creating bucket '{bucket}'. Details: {exc}"
                )
                log.error(msg)

                raise exc
        else:
            log.warning(f"Bucket '{bucket}' already exists.")

        file_exists_in_bucket: bool = minio_client.stat_object(
            bucket_name=bucket, object_name=dst_file
        )

        if not file_exists_in_bucket:
            log.debug(f"Uploading file '{src_file}' to '(bucket:{bucket}):{dst_file}'.")
            try:
                minio_client.fput_object(bucket, dst_file, src_file)
                log.success(f"Uploaded '{src_file}' to (bucket:{bucket}):{dst_file}")
            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception uploading file '{src_file}' to '(bucket:{bucket}):{dst_file}'. Details: {exc}"
                )
                log.error(msg)

                raise exc
        else:
            log.warning(
                f"File '{Path(src_file).name}' already exists in bucket '(bucket:{bucket}): {dst_file}'. Skipping upload."
            )