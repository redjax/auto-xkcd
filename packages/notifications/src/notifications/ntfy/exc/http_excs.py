import logging

import typing as t

log = logging.getLogger(__name__)

__all__ = ["CloudflareBlockException", "NtfyFileAttachmentsNotConfiguredError"]


ntfy_exc_msg: str = """File uploads are not configured on the remote ntfy server.

If you are the Ntfy server administrator, set the 'attachment-cache-dir' and \
'attachment-file-size-limit' vars in your server.yml.

If Ntfy is running in Docker, set the env variables:

- NTFY_ATTACHMENT_CACHE_DIR=/var/lib/ntfy/attachments
- NTFY_ATTACHMENT_TOTAL_SIZE_LIMIT=5G
- NTFY_ATTACHMENT_FILE_SIZE_LIMIT=15M
- NTFY_ATTACHMENT_EXPIRY_DURATION=3h
"""


class CloudflareBlockException(Exception):
    """Exception for requests blocked by Cloudflare.

    Description:
        If a response's status code is 403, and the text 'cloudflare' or '<title>Attention Required! | Cloudflare</title>' is in the response's text,
        the request was blocked by Cloudflare.
    """

    def __init__(self, message: str = "Request was blocked by Cloudflare."):
        self.message = message
        super().__init__(message)


class NtfyFileAttachmentsNotConfiguredError(Exception):
    """Exception for requests to a Ntfy server that are blocked because file attachments are not configured on the remote.

    Description:
        If a response's status code is 400, and the text 'attachments not allowed' is in the response's text, the request
        was blocked because the remote Ntfy server is not configured to accept file attachments.

        If you are the owner of the remote Ntfy server, you can fix this using one of the methods below:
            - Edit your server.yml, set the following variables:
                - `attachment-cache-dir=/var/lib/ntfy/attachments`
                - `attachment-file-size-limit=5G`
            - Set the following environment variables:
                - `NTFY_ATTACHMENT_CACHE_DIR=/var/lib/ntfy/attachments`
                - `NTFY_ATTACHMENT_TOTAL_SIZE_LIMIT=5G`
                - `NTFY_ATTACHMENT_FILE_SIZE_LIMIT=15M`
                - `NTFY_ATTACHMENT_EXPIRY_DURATION=3h`
    """

    def __init__(self, message: str = ntfy_exc_msg):
        self.message = message
        super().__init__(message)
