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


class XkcdComicImageRepository(db_lib.base.BaseRepository[XkcdComicModel]):
    def __init__(self, session: so.Session):
        super().__init__(session, XkcdComicImageModel)