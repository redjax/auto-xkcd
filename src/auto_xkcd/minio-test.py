from __future__ import annotations

from pathlib import Path

from core import (
    AppSettings,
    DBSettings,
    MinioSettings,
    _exc,
    database,
    db_settings,
    get_db,
    minio_settings,
    settings,
)
import httpx
from loguru import logger as log
import minio
from minio.datatypes import Bucket
from modules import minio_mod
from red_utils.ext.loguru_utils import init_logger, sinks

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

    log.debug(f"Endpoint: {minio_settings.endpoint}")

    with minio_mod.get_minio_controller(
        minio_settings=minio_settings
    ) as minio_controller:
        client = minio_controller.client

        log.info("Listing buckets")

        minio_client: minio.Minio = minio_controller.client

        try:
            buckets: list[Bucket] = minio_client.list_buckets()
            log.success(f"Buckets: {buckets}")
        except Exception as exc:
            msg = Exception(f"Unhandled exception listing buckets. Details: {exc}")
            log.error(msg)

            raise exc

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

                # raise exc
        else:
            log.warning(f"Bucket '{bucket}' already exists.")

        try:
            file_exists_in_bucket: bool = minio_client.stat_object(
                bucket_name=bucket, object_name=dst_file
            )
        except _exc.S3Error as s3_err:
            log.warning(
                f"File '{Path(src_file).name}' does not exist in remote '(bucket:{bucket}):{dst_file}'."
            )
            file_exists_in_bucket = False

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception checking for existence of file '{src_file}' in bucket '{bucket}'. Details ({type(exc)}): {exc}"
            )
            log.warning(msg)

            file_exists_in_bucket = False

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
