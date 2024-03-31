import minio
from minio.datatypes import Bucket

from loguru import logger as log


def get_buckets(minio_client: minio.Minio = None) -> list[Bucket]:
    assert minio_client, ValueError("Missing a minio client")
    assert isinstance(minio_client, minio.Minio), TypeError(
        f"minio_client must be a minio.Minio object. Got type: ({type(minio_client)})"
    )

    try:
        buckets: list[Bucket] = minio_client.list_buckets()

        if buckets:
            log.success(f"Retrieved buckets.")
            return buckets

        else:
            log.warning(f"Connection success, but no buckets found.")
            return []

    except Exception as exc:
        msg = Exception(f"Unhandled exception listing buckets. Details: {exc}")
        log.error(msg)

        raise exc


def bucket_exists(minio_client: minio.Minio = None, bucket_name: str = None) -> bool:
    assert minio_client, ValueError("Missing a minio client")
    assert isinstance(minio_client, minio.Minio), TypeError(
        f"minio_client must be a minio.Minio object. Got type: ({type(minio_client)})"
    )

    assert bucket_name, ValueError("Missing a bucket name")
    assert isinstance(bucket_name, str), TypeError(
        f"bucket_name must be a string. Got type: ({type(bucket_name)})"
    )

    try:
        found: bool = minio_client.bucket_exists(bucket_name=bucket_name)

        return found
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception checking for existence of bucket '{bucket_name}'. Details: {exc}"
        )
        log.error(msg)

        raise msg
