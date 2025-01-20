from loguru import logger as log
import typing as t

import db_lib
from .models import XkcdComicImageModel, XkcdComicModel

import sqlalchemy as sa
import sqlalchemy.orm as so
import sqlalchemy.exc as sa_exc


class XkcdComicRepository(db_lib.base.BaseRepository[XkcdComicModel]):
    def __init__(self, session: so.Session):
        super().__init__(session, XkcdComicModel)
        
    def get_by_num(self, comic_num: int) -> XkcdComicModel | None:
        return self.session.query(XkcdComicModel).filter(XkcdComicModel.num == comic_num).one_or_none()
    
    def get_multiple_by_num(self, comic_nums: list[int]) -> list[XkcdComicModel] | None:
        return self.session.query(XkcdComicModel).filter(XkcdComicModel.num.in_(comic_nums)).all()


class XkcdComicImageRepository(db_lib.base.BaseRepository[XkcdComicModel]):
    def __init__(self, session: so.Session):
        super().__init__(session, XkcdComicImageModel)
        
    def get_by_num(self, comic_num: int) -> XkcdComicImageModel | None:
        return self.session.query(XkcdComicImageModel).filter(XkcdComicImageModel.num == comic_num).one_or_none()

    def get_multiple_by_num(self, comic_nums: list[int]) -> list[XkcdComicImageModel] | None:
        return self.session.query(XkcdComicImageModel).filter(XkcdComicImageModel.num.in_(comic_nums)).all()