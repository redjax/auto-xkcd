import logging
import base64

from pydantic import BaseModel, Field

log = logging.getLogger(__name__)

__all__ = ["NtfyConfig"]


class NtfyConfig(BaseModel):
    server: str
    topic: str
    user: str | None = Field(default=None)
    password: str | None = Field(default=None, repr=False)
    token: str | None = Field(repr=False)

    @property
    def default_headers(self) -> dict:
        return {"Content-Type": "application/json", "Accept": "application/json"}

    @property
    def auth_headers(self) -> dict:
        if self.token:
            auth_headers: dict = {"Authorization": f"Bearer {self.token}"}
        elif self.user and self.password:
            auth_header_encoded = (
                "Basic "
                + base64.b64encode(f"{self.user}:{self.password}".encode()).decode()
            )

            auth_headers: dict = {"Authorzation": auth_header_encoded}
        else:
            if (self.user is None or self.password is None) and self.token is None:
                log.warning("Must pass either a username AND password, OR a token.")

            auth_headers = {}

        return auth_headers

    @property
    def url(self) -> str:
        _url = f"{self.server}/{self.topic}"

        return _url

    def get_headers(self, extra_headers: dict | None = {}) -> dict:
        return self.auth_headers | self.default_headers | extra_headers
