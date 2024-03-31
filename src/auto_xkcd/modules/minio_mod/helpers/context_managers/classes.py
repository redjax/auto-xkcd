from __future__ import annotations

from contextlib import AbstractContextManager
from pathlib import Path
import typing as t

from core import _exc

from loguru import logger as log
import minio
from minio import datatypes as minio_dtypes
from minio.commonconfig import Tags
from minio.credentials import Provider
from minio.deleteobjects import DeleteObject
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

    def get_buckets(self) -> list[minio_dtypes.Bucket]:
        """Return list of all buckets in minio storage."""
        if not self.client:
            log.warning(f"Client has not been intialized. Returning empty list.")
            return []

        try:
            buckets: list[minio_dtypes.Bucket] = self.client.list_buckets()

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

    def bucket_exists(self, bucket_name: str = None) -> bool:
        if not self.client:
            log.warning(f"Client has not been intialized. Returning empty list.")
            return

        assert bucket_name, ValueError("Missing a bucket name")
        assert isinstance(bucket_name, str), TypeError(
            f"bucket_name must be a string. Got type: ({type(bucket_name)})"
        )

        try:
            found: bool = self.client.bucket_exists(bucket_name=bucket_name)

            return found
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception checking for existence of bucket '{bucket_name}'. Details: {exc}"
            )
            log.error(msg)

            raise msg

    def create_bucket(self, bucket_name: str = None) -> bool:
        assert bucket_name, ValueError("Missing a bucket name")
        assert isinstance(bucket_name, str), TypeError(
            f"bucket_name should be a string. Got type: ({type(bucket_name)})"
        )

        try:
            found: bool = self.client.bucket_exists(bucket_name=bucket_name)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception creating bucket '{bucket_name}'. Details: {exc}"
            )
            log.error(msg)

            return

        if not found:
            try:
                self.client.make_bucket(bucket_name=bucket_name)
                log.success(f"Bucket created: {bucket_name}")

                return True

            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception creating bucket '{bucket_name}'. Details: {exc}"
                )
                log.error(msg)

                return

        else:
            log.warning(f"Bucket '{bucket_name}' already exists.")
            return True

    def file_exists_in_bucket(
        self, bucket_name: str = None, object_path: str = None
    ) -> bool:
        assert bucket_name, ValueError("Missing a bucket name")
        assert isinstance(bucket_name, str), TypeError(f"bucket_name must be a string.")

        assert object_path, ValueError("Missing a filename to search")
        assert isinstance(object_path, str), TypeError(
            f"object_path must be a string. Got type: ({type(object_path)})"
        )

        try:
            file_exists_in_bucket: minio_dtypes.Object = self.client.stat_object(
                bucket_name=bucket_name, object_name=object_path
            )

            return True
        except _exc.S3Error as s3_err:
            log.error(f"S3Error: {s3_err}")
            log.warning(
                f"File '{Path(object_path).name}' does not exist in remote '(bucket:{bucket_name}):{object_path}'."
            )
            file_exists_in_bucket = False

            return False

        except Exception as exc:
            msg = Exception(
                f"Unhandled exception checking for existence of file '{object_path}' in bucket '{bucket_name}'. Details ({type(exc)}): {exc}"
            )
            log.warning(msg)

            raise exc

    def _create_obj_tags(
        self,
        tag_dicts: list[dict[str, str]] = None,
    ) -> Tags:
        assert tag_dicts, ValueError("Missing a list of tag dicts")
        assert isinstance(tag_dicts, list), TypeError(
            f"tag_dicts must be a list of tag dicts. Got type: ({type(tag_dicts)})"
        )
        tags: Tags = Tags.new_object_tags()

        for t_dict in tag_dicts:
            log.debug(f"Adding tag: {t_dict}")
            for k, v in t_dict.items():
                tags[k] = v

        return tags

    def upload_file(
        self, bucket_name: str = None, src_file: str = None, dest_file: str = None
    ) -> bool:
        """References:
        https://github.com/minio/minio-py/blob/master/examples/fput_object.py
        https://github.com/minio/minio-py/blob/master/examples/put_object.py
        """
        file_exists_in_bucket: bool = self.file_exists_in_bucket(
            bucket_name=bucket_name, object_path=dest_file
        )

        if not file_exists_in_bucket:
            log.debug(
                f"Uploading file '{src_file}' to '(bucket:{bucket_name}):{dest_file}'."
            )
            try:
                self.client.fput_object(bucket_name, dest_file, src_file)
                log.success(
                    f"Uploaded '{src_file}' to (bucket:{bucket_name}):{dest_file}"
                )

                return True

            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception uploading file '{src_file}' to '(bucket:{bucket_name}):{dest_file}'. Details: {exc}"
                )
                log.error(msg)

                # raise exc

                return False
        else:
            log.warning(
                f"File '{Path(src_file).name}' already exists in bucket '(bucket:{bucket_name}): {dest_file}'. Skipping upload."
            )

            return False

    def set_obj_tags(
        self,
        tags: t.Union[list[dict[str, str]], Tags] = None,
        bucket_name: str = None,
        object_path: str = None,
    ):
        assert tags, ValueError("Missing object tags")
        assert isinstance(tags, list) or isinstance(tags, Tags), TypeError(
            f"tags must be of type minio.Tags or list[dict]. Got type: ({type(tags)})"
        )
        assert bucket_name, ValueError("Missing a bucket name")
        assert isinstance(bucket_name, str), TypeError(
            f"bucket_name must be a string. Got type: ({type(bucket_name)})"
        )

        assert object_path, ValueError("Missing path to object in bucket.")
        assert isinstance(object_path, str), TypeError(
            f"object_path must be a string. Got type: ({type(object_path)})"
        )

        if isinstance(tags, list):
            try:
                _tags = self._create_obj_tags(tag_dicts=tags)
                tags: Tags = _tags
            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception creating minio.Tags object. Details: {exc}"
                )
                log.error(msg)

                return

        log.info(
            f"Setting tags {tags.items()} on object '(bucket:{bucket_name}'):{object_path}'"
        )
        try:
            self.client.set_object_tags(
                bucket_name=bucket_name, object_name=object_path, tags=tags
            )
            log.success(f"Tagged object {object_path}")

            return True
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception setting tags on object. Details: {exc}"
            )
            log.error(msg)

            raise exc

    def get_bucket_tags(self, bucket_name: str = None) -> list[Tags]:
        assert bucket_name, ValueError("Missing a bucket name")
        assert isinstance(bucket_name, str), TypeError(
            f"bucket_name must be a string. Got type: ({type(bucket_name)})"
        )

        try:
            tags = self.client.get_bucket_tags(bucket_name=bucket_name)

            return tags
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception getting tags for bucket '{bucket_name}'. Details: {exc}"
            )
            log.error(msg)

            raise exc

    def delete_obj(self, bucket_name: str = None, object_path: str = None):
        """https://github.com/minio/minio-py/blob/master/examples/remove_objects.py"""
        assert bucket_name, ValueError("Missing a bucket name")
        assert isinstance(bucket_name, str), TypeError(
            f"bucket_name must be a string. Got type: ({type(bucket_name)})"
        )

        assert object_path, ValueError("Missing an object path")
        assert isinstance(object_path, str), TypeError(
            f"object_path must be a string. Got type: ({type(object_path)})"
        )

        try:
            self.client.remove_object(bucket_name=bucket_name, object_name=object_path)
            log.success(f"Deleted file '(bucket:{bucket_name}):{object_path}'")

            return True
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception removing object '(bucket:{bucket_name}): {object_path}'. Details: {exc}"
            )
            log.error(msg)

            return False

    def get_objects(
        self, bucket_name: str = None, recursive: bool = True, prefix: str = None
    ):
        """https://github.com/minio/minio-py/blob/master/examples/list_objects.py"""

        raise NotImplementedError(f"Listing objects in a bucket is not yet supported")
        assert bucket_name, ValueError("Missing a bucket name")
        assert isinstance(bucket_name, str), TypeError(
            f"bucket_name must be a string. Got type: ({type(bucket_name)})"
        )

    def download_file(self, bucket_name: str = None, object_path: str = None):
        """https://github.com/minio/minio-py/blob/master/examples/fget_object.py"""
        raise NotImplementedError("Downloading a single file is not yet supported.")

    def download_file(self, bucket_name: str = None, object_path: str = None):
        """https://github.com/minio/minio-py/blob/master/examples/get_object.py"""
        raise NotImplementedError(f"Downloading objects is not yet implemented")
        assert bucket_name, ValueError("Missing a bucket name")
        assert isinstance(bucket_name, str), TypeError(
            f"bucket_name must be a string. Got type: ({type(bucket_name)})"
        )

    def copy_obj():
        """https://github.com/minio/minio-py/blob/master/examples/copy_object.py"""
        raise NotImplementedError("Copying objects is not yet supported.")
