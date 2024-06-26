from __future__ import annotations

import datetime
import typing as t

from core.constants import XKCD_URL_BASE, XKCD_URL_POSTFIX
import pendulum
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    computed_field,
    field_validator,
)
from red_utils.ext import time_utils
from red_utils.std import hash_utils
from utils.list_utils import prepare_list_shards

class ComicNumCSVData(BaseModel):
    """Store metadata about a comic number, like if the image has been saved.

    Params:
        comic_num (int|str): An XKCD comic number.
        img_saved (bool): Whether or not `.png` of comic has been saved.

    """

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
    """Structured data about the current XKCD comic.

    Params:
        comic_num (int|str): The XKCD comic's entry number.
        last_updated (datetime.datetime, datetime.date, pendulum)
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    comic_num: t.Union[int, str] | None = Field(default=None)
    last_updated: t.Union[datetime.datetime, pendulum.DateTime] | None = Field(
        default=None
    )

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
    def validate_date_sent(cls, v) -> pendulum.DateTime:
        if v is None:
            return None

        if isinstance(v, pendulum.DateTime):
            return v

        else:
            if isinstance(v, datetime.datetime):
                d: pendulum.DateTime = pendulum.instance(obj=v)

                return d

            elif isinstance(v, str):
                d = pendulum.parse(text=v)

        raise ValidationError

    def overwrite_last_updated(self) -> t.Self:
        """Set/re-set class's .last_updated value."""
        ts: str | pendulum.DateTime = time_utils.get_ts()

        self.last_updated = ts

        return self


class XKCDComicBase(BaseModel):
    year: str = Field(default=None)
    month: str = Field(default=None)
    day: str = Field(default=None)
    ## XKCD's API responds with 'num,' but I use 'comic_num'.
    #  Set priority 2 on alias so DB model validation works
    comic_num: int = Field(default=None, alias="num", alias_priorty=2)
    # link: str | None = Field(default=None)
    title: str = Field(default=None)
    transcript: str | None = Field(default=None)
    alt_text: str = Field(default=None, alias="alt")
    img_url: str = Field(default=None, alias="img")
    # img_bytes: bytes | None = Field(default=None, repr=False)
    img_saved: bool | None = Field(default=False)

    @property
    def telegram_msg(self) -> str:
        """Return a formatted message string for Telegram messages."""
        msg: str = f"""Current XKCD Comic

Date: {self.month}-{self.day}-{self.year}
Title: {self.title}
Comic Number: {self.comic_num}
Transcript: {self.transcript}
Alt: {self.alt_text}
Link: {self.img_url}
"""

        return msg

    @computed_field
    @property
    def link(self) -> str:
        _link: str = f"{XKCD_URL_BASE}/{self.comic_num}"

        return _link

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
    """XKCD comic data retrieved from the XKCD API.

    Params:
        year (str): Published year
        month (str): Published month
        day (str): Published day
        comic_num (int): XKCD comic number
        title (str): XKCD comic title
        transcript (str): XKCD comic transcript
        alt_text (str): XKCD comic alt text
        img_url (str): XKCD comic's image URL
        [DISABLED] img_bytes (bytes): XKCD comic image bytes. Initialized as `None` and populated once the image is requested.

    """

    pass


class XKCDComicImageBase(BaseModel):

    comic_num: int = Field(default=None)
    img: bytes = Field(default=None)


class XKCDComicImage(XKCDComicImageBase):
    pass


class XKCDComicImageOut(XKCDComicImageBase):
    pass


class XKCDComicOut(XKCDComicBase):
    """Append the XKCD comic's database ID."""

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
    """Metadata class for comics sent via Telegram.

    Params:
        comic_num (int): The XKCD comic's number
        date_sent (datetime.datetime|datetime.date|pendulum.DateTime|pendulum.Date): Timestamp for when the comic was sent via Telegram.

    """

    pass


class XKCDSentComicOut(XKCDSentComicBase):
    sent_comic_id: int


class MultiComicRequestQueue(BaseModel):
    queue: list[int] | list[list] = Field(default=None)
    partitioned: bool = Field(default=False)
    max_queue_size: int = Field(default=15)

    @property
    def queue_size(self) -> int:
        if self.queue is None:
            return 0
        elif isinstance(self.queue[0], int):
            return len(self.queue)
        elif isinstance(self.queue[0], list):
            queue_count = 0

            for q in self.queue:
                queue_count += 1

            return queue_count

    def partition_queue(self) -> list[int] | list[list[int]]:
        _partitioned: list[list[int]] = prepare_list_shards(original_list=self.queue)

        if isinstance(_partitioned[0], list):
            self.queue = _partitioned
            self.partitioned = True

        return _partitioned
