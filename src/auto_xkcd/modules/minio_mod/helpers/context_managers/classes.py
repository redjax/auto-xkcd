from __future__ import annotations

from contextlib import AbstractContextManager
from pathlib import Path
import typing as t

from loguru import logger as log
import minio
from minio import datatypes as minio_dtypes
from minio.credentials import Provider
from minio.error import (
    InvalidResponseError,
    MinioAdminException,
    MinioException,
    S3Error,
    ServerError,
)

class MinioController(AbstractContextManager):
    def __init__(
        self,
        endpoint: str,
        secure: bool,
        access_key: str,
        secret_key: str,
        region: str | None = None,
        session_token: str | None = None,
        credentials: Provider | None = None,
        cert_check: bool = False,
    ) -> None:
        self.endpoint: str = endpoint
        self.secure: bool = secure
        self.cert_check: bool = cert_check
        self.access_key: str | None = access_key
        self.secret_key: str = secret_key
        self.session_token: str | None = session_token
        self.region: str | None = region
        self.credentials: Provider | None = credentials

        self.client = None

    def __repr__(self):
        return f"MinioController(endpoint={self.endpoint!r}, secure={self.secure!r}, cert_check={self.cert_check!r}, access_key={self.access_key!r}, region={self.region!r}, credentials={self.credentials!r})"

    def __enter__(self):
        _client: minio.Minio = minio.Minio(
            endpoint=self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure,
        )

        if self.session_token:
            _client.session_token = self.session_token
        if self.region:
            _client.region = self.region
        if self.credentials:
            _client.credentials = self.credentials

        self.client: minio.Minio = _client

        return self

    def __exit__(self, exc_type, exc_val, traceback):
        if exc_type:
            log.error(f"({exc_type}): {exc_val}")
        if traceback:
            log.trace(traceback)

        self.client = None
