from __future__ import annotations

import logging

from domain.ntfy.base import BaseAction

from pydantic import BaseModel, Field, ValidationError, computed_field, field_validator

log = logging.getLogger(__name__)

__all__ = ["ViewAction", "BroadcastAction", "HttpAction"]


class ViewAction(BaseAction):
    @computed_field
    @property
    def action(self) -> str:
        return "view"

    @computed_field
    @property
    def action_header(self) -> str:
        return f"action={self.action}, label={self.label}, url={self.url}, clear={self.clear}"


class BroadcastAction(BaseAction):
    label: str
    intent: str = Field(default="io.heckel.ntfy.USER_ACTION")
    extras: dict[str, str] | None = Field(default=None)
    clear: bool = Field(default=False)

    @computed_field
    @property
    def action(self) -> str:
        return "broadcast"

    @computed_field
    @property
    def action_header(self) -> str:
        action_str = f"action={self.action}, label={self.label}, url={self.url}, clear={self.clear}, intent={self.intent}"

        if self.extras:
            action_str += "".format(self.extras)

        return action_str


class HttpAction(BaseAction):
    label: str
    url: str
    method: str = Field(default="POST")
    headers: dict[str, str] | None = Field(default=None)
    body: str | None = Field(default=None)
    clear: bool = Field(default=False)

    @computed_field
    @property
    def action(self) -> str:
        return "http"

    @computed_field
    @property
    def action_header(self) -> str:
        action_str = f"action={self.action}, label={self.label}, url={self.url}, method={self.method}, clear={self.clear}"

        if self.headers is not None:
            headers = ""
            for k, v in self.headers.items():
                headers += f"headers.{k}={v}"

            action_str = f", {headers}"

        if self.body:
            action_str += f", body={self.body}"

        log.debug(action_str)

        return action_str
