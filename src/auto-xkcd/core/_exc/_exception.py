from __future__ import annotations

from minio.error import (
    InvalidResponseError,
    MinioAdminException,
    MinioException,
    S3Error,
    ServerError,
)
from urllib3.exceptions import (
    DecodeError,
    HostChangedError,
    MaxRetryError,
    NameResolutionError,
    NewConnectionError,
    PoolError,
    ProtocolError,
    ProxyError,
    ReadTimeoutError,
    RequestError,
    ResponseError,
    TimeoutError,
)
