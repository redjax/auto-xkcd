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
        log.info("Listing buckets")

        buckets: list[Bucket] = minio_controller.get_buckets()
        log.debug(f"Buckets: {buckets}")

        ## Create bucket if it doesn't exist
        minio_controller.create_bucket(bucket_name=bucket)

        ## Upload a file. Skip if file exists in bucket
        minio_controller.upload_file(
            bucket_name=bucket, src_file=src_file, dest_file=dst_file
        )

        ## Set a tag on an object
        minio_controller.set_obj_tags(
            tags=[{"test": "true"}], bucket_name=bucket, object_path=dst_file
        )

        ## Delete the test file
        minio_controller.delete_obj(bucket_name=bucket, object_path=dst_file)
        log.debug(
            f"File exists after deletion: {minio_controller.file_exists_in_bucket(bucket_name=bucket, object_path=dst_file)}"
        )

        ## Re-create file && check for existence again
        try:
            minio_controller.upload_file(
                bucket_name=bucket, src_file=src_file, dest_file=dst_file
            )
            log.debug(
                f"File exists after shenanigans: {minio_controller.file_exists_in_bucket(bucket_name=bucket, object_path=dst_file)}"
            )
        except Exception as exc:
            msg = Exception(f"Unhandled exception uploading file. Details: {exc}")
            log.error(msg)
