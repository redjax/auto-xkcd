from core import (
    MinioSettings,
    minio_settings,
    settings,
    AppSettings,
    db_settings,
    DBSettings,
)
from core import database, get_db, get_minio_client

from loguru import logger as log
from red_utils.ext.loguru_utils import init_logger, sinks
import minio

import httpx

if __name__ == "__main__":
    init_logger(sinks=[sinks.LoguruSinkStdErr(level=settings.log_level).as_dict()])

    log.info(f"[env:{settings.env}|container:{settings.container_env}] Start auto-xkcd")

    log.debug(f"Settings: {settings}")
    log.debug(f"DB settings: {db_settings}")
    log.debug(f"Minio settings: {minio_settings}")
    log.debug(
        f"Minio access:\n\tKey: {minio_settings.access_key}\n\tSecret: {minio_settings.access_secret}"
    )

    # minio_client: minio.Minio = minio.Minio(
    #     endpoint=minio_settings.endpoint,
    #     secure=minio_settings.secure,
    #     access_key=minio_settings.access_key,
    #     secret_key=minio_settings.access_secret,
    # )

    log.info("Attempting to upload testfile.txt")
    src_file = "testfile.txt"
    bucket = "auto-xkcd"
    dst_file = "testfile.txt"

    with get_minio_client() as minio_client:
        ## Create bucket if it doesn't exist
        found = minio_client.bucket_exists(bucket)
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

        log.debug(f"Uploading file '{src_file}' to '({bucket}):{dst_file}'.")
        try:
            minio_client.fput_object(bucket, dst_file, src_file)
            log.success(f"Uploaded '{src_file}' to ({bucket}):{dst_file}")
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception uploading file '{src_file}' to '({bucket}):{dst_file}'. Details: {exc}"
            )
            log.error(msg)

            raise exc
