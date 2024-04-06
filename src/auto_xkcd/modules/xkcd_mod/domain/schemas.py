from __future__ import annotations

import datetime
import typing as t

import pendulum
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    computed_field,
    field_validator,
)
from red_utils.std import hash_utils
from red_utils.ext import time_utils


class ComicNumCSVData(BaseModel):
    comic_num: t.Union[int, str] = Field(default=None)
    img_saved: bool = Field(default=False)

    @field_validator("comic_num")
    def validate_comic_num(cls, v) -> int:
        if isinstance(v, int):
            return v

        if isinstance(v, str):
            try:
                return int(v)
            except Exception as exc:
                raise Exception(f"Unable to convert string to int: '{v}'.")

        raise ValidationError


class CurrentComicMeta(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    comic_num: t.Union[int, str] | None = Field(default=None)
    last_updated: (
        t.Union[datetime.datetime, datetime.date, pendulum.DateTime, pendulum.Date]
        | None
    ) = Field(default=None)

    @field_validator("comic_num")
    def validate_comic_num(cls, v) -> int:
        if v is None:
            return None

        if isinstance(v, int):
            return v

        if isinstance(v, str):
            try:
                return int(v)
            except Exception as exc:
                raise Exception(f"Unable to convert string to int: '{v}'.")

        raise ValidationError

    @field_validator("last_updated")
    def validate_date_sent(cls, v) -> pendulum.Date:
        if v is None:
            return None

        if isinstance(v, pendulum.Date):
            if isinstance(v, pendulum.DateTime):
                return v.date()
            return v
        else:
            if isinstance(v, datetime.datetime):
                d = pendulum.instance(v).date()

                return d
            elif isinstance(v, datetime.date):
                d = pendulum.instance(v)

                return d
            elif isinstance(v, str):
                d = pendulum.parse(v).date()

        raise ValidationError

    def overwrite_last_updated(self):
        ts: str | pendulum.DateTime = time_utils.get_ts()

        self.last_updated = ts

        return self


class XKCDComicBase(BaseModel):
    year: str = Field(default=None)
    month: str = Field(default=None)
    day: str = Field(default=None)
    comic_num: int = Field(default=None, alias="num")
    link: str | None = Field(default=None)
    title: str = Field(default=None)
    transcript: str | None = Field(default=None)
    alt_text: str = Field(default=None, alias="alt")
    img_url: str = Field(default=None, alias="img")
    img: bytes = Field(default=None, repr=False)

    @property
    def telegram_msg(self) -> str:
        """Return a formatted message string for Telegram messages."""
        msg: str = f"""XKCD Comic for {self.month}-{self.day}-{self.year}

Title: {self.title}
Comic Number: {self.comic_num}
Transcript: {self.transcript}
Alt: {self.alt_text}
Link: {self.img_url}
"""

        return msg

    @computed_field
    @property
    def comic_num_hash(self) -> str:
        try:
            _hash: str = hash_utils.get_hash_from_str(input_str=str(self.comic_num))

            return _hash
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception getting hash from comic num ({type(self.comic_num)}): {self.comic_num}. Details: {exc}"
            )

            raise msg


class XKCDComic(XKCDComicBase):
    pass


class XKCDComicOut(XKCDComicBase):
    comic_id: int


class XKCDSentComicBase(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    comic_num: int = Field(default=None)
    date_sent: t.Union[
        datetime.datetime, datetime.date, pendulum.DateTime, pendulum.Date
    ] = Field(default=None)

    @field_validator("date_sent")
    def validate_date_sent(cls, v) -> pendulum.Date:
        if isinstance(v, pendulum.Date):
            if isinstance(v, pendulum.DateTime):
                return v.date()
            return v
        else:
            if isinstance(v, datetime.datetime):
                d = pendulum.instance(v).date()

                return d
            elif isinstance(v, datetime.date):
                d = pendulum.instance(v)

                return d
            elif isinstance(v, str):
                d = pendulum.parse(v).date()

        raise ValidationError


class XKCDSentComic(XKCDSentComicBase):
    pass


class XKCDSentComicOut(XKCDSentComicBase):
    sent_comic_id: int
