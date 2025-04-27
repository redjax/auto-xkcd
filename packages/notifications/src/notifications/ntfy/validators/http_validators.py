import logging
from dataclasses import dataclass, field

from notifications.ntfy.exc.http_excs import (
    NtfyFileAttachmentsNotConfiguredError,
    CloudflareBlockException,
)

import httpx

log = logging.getLogger(__name__)

__all__ = [
    "HttpResponseValidator",
    "response_is_cloudflare_blocked",
    "response_is_ntfy_file_attachment_not_configured_error",
]


@dataclass
class HttpResponseValidator:
    """Run an httpx.Response through a series of custom validators."""

    response: httpx.Response
    raise_exceptions: bool = field(
        default=False,
    )
    exc_type: str | None = field(default=None)
    exc_message: str | None = field(default=None)

    def __post_init__(self):
        if self.response is None:
            raise ValueError(
                "HttpResponseValidator.response must be an httpx.Response object."
            )

    def is_cloudflare_blocked(self) -> bool:
        blocked = response_is_cloudflare_blocked(self.response)
        if blocked:
            if self.raise_exceptions:
                raise CloudflareBlockException()

        return blocked

    def is_ntfy_file_attachment_not_configured_error(self) -> bool:
        blocked = response_is_ntfy_file_attachment_not_configured_error(self.response)
        if blocked:
            if self.raise_exceptions:
                raise NtfyFileAttachmentsNotConfiguredError()

        return blocked

    def validate(self) -> bool:
        if self.is_cloudflare_blocked():
            log.error(CloudflareBlockException())

            return True

        if self.is_ntfy_file_attachment_not_configured_error():
            log.error(NtfyFileAttachmentsNotConfiguredError())

            return True

        return False


def response_is_cloudflare_blocked(
    res: httpx.Response, raise_early: bool = False
) -> bool:
    """Test a response to see if request was blocked by Cloudflare.

    Params:
        res (httpx.Response): An httpx.Response object to evaluate.
        raise_early (bool): If `True`, raise exception instead of returning False.

    Returns:
        (bool): `True` when response was blocked by Cloudflare.
        (bool): `False` when response was not blocked by Cloudflare.

    Raises:
        (ntfy_client.exc.CloudflareBlockException): Custom exception for requests blocked by Cloudflare.
    """
    if (
        res.status_code == 403
        and ("cloudflare" or "<title>Attention Required! | Cloudflare</title>")
        in res.text.lower()
    ):
        log.debug(f"Request was blocked by Cloudflare. Details: {res.text}")

        if raise_early:
            raise CloudflareBlockException("Request was blocked by Cloudflare.")
        return True
    else:
        log.debug("Request was not blocked by Cloudflare.")
        return False


def response_is_ntfy_file_attachment_not_configured_error(
    res: httpx.Response, raise_early: bool = False
) -> bool:
    """Test a response to see if the request errored due to file attachments not being configured on the remote ntfy server.

    Params:
        res (httpx.Response): An httpx.Response object to evaluate.
        raise_early (bool): If `True`, raise exception instead of returning False.

    Returns:
        (bool): `True` when response was blocked by Cloudflare.
        (bool): `False` when response was not blocked by Cloudflare.

    Raises:
        (ntfy_client.exc.CloudflareBlockException): Custom exception for requests blocked by Cloudflare.

    """
    if res.status_code == 400 and "attachments not allowed" in res.text.lower():
        log.debug("File attachments are not configured on the remote ntfy server.")

        if raise_early:
            raise NtfyFileAttachmentsNotConfiguredError()

        return True
    else:
        log.debug(
            "Error response was not related to ntfy file attachments being configured on the remote server"
        )

        return False
