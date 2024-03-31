from urllib3.exceptions import (
    MaxRetryError,
    NameResolutionError,
    NewConnectionError,
    PoolError,
    ProtocolError,
    ProxyError,
    DecodeError,
    RequestError,
    TimeoutError,
    ResponseError,
    HostChangedError,
    ReadTimeoutError,
)
from minio.error import (
    S3Error,
    MinioAdminException,
    MinioException,
    ServerError,
    InvalidResponseError,
)
