from __future__ import annotations

import datetime as dt
import typing as t

from .constants import XKCD_URL_BASE

from core_utils import hash_utils
from loguru import logger as log
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    computed_field,
    field_validator,
)

class XkcdComicImgBase(BaseModel):
    num: t.Union[str, int] = Field(default=None)
    img_bytes: bytes = Field(default=None, repr=False)
    
    
class XkcdComicImgIn(XkcdComicImgBase):
    pass


class XkcdComicImgOut(XkcdComicImgBase):
    id: int
    

class XkcdComicBase(BaseModel):
    year: str = Field(default=None)
    month: str = Field(default=None)
    day: str = Field(default=None)
    num: int = Field(default=None)
    title: str = Field(default=None)
    transcript: str | None = Field(default=None)
    alt_text: str = Field(default=None, alias="alt")
    img_url: str = Field(default=None, alias="img")
    
    @computed_field
    @property
    def link(self) -> str:
        _link: str = f"{XKCD_URL_BASE}/{self.num}"

        return _link

    @computed_field
    @property
    def comic_num_hash(self) -> str:
        try:
            _hash: str = hash_utils.get_hash_from_str(input_str=str(self.num))

            return _hash
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception getting hash from comic num ({type(self.num)}): {self.num}. Details: {exc}"
            )

            raise msg
        

class XkcdComicIn(XkcdComicBase):
    pass


class XkcdComicOut(XkcdComicBase):
    id: int
    
    img_saved: bool


class XkcdApiResponseBase(BaseModel):
    response_content: dict = Field(default=None, repr=False)
    
    def return_comic_obj(self) -> XkcdComicIn:
        if not self.response_content:
            raise ValueError("XkcdComicIn.response_content cannot be None")
        
        try:
            comic: XkcdComicIn = XkcdComicIn.model_validate(self.response_content)
            
            return comic
        except Exception as exc:
            msg = f"({type(exc)}) Error converting response content to XkcdComicIn object. Details: {exc}"
            log.error(msg)
            
            raise exc

    
class XkcdApiResponseIn(XkcdApiResponseBase):
    pass


class XkcdApiResponseOut(XkcdApiResponseBase):
    id: int


class XkcdComicWithImgBase(BaseModel):
    comic: XkcdComicIn
    comic_img: XkcdComicImgIn

    @property
    def num(self) -> int:
        return self.comic.num
    
    @property
    def img_url(self) -> str:
        return self.comic.img_url


class XkcdComicWithImgIn(XkcdComicWithImgBase):
    pass


class XkcdComicWithImgOut(XkcdComicWithImgBase):
    id: int


class XkcdCurrentComicMetadataBase(BaseModel):
    num: int
    last_updated: t.Union[str, dt.datetime]
    

class XkcdCurrentComicMetadataIn(XkcdCurrentComicMetadataBase):
    pass


class XkcdCurrentComicMetadataOut(XkcdCurrentComicMetadataBase):
    id: int
