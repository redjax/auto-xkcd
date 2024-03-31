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
