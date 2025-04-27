from __future__ import annotations

from datetime import datetime

import db_lib
from loguru import logger as log
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as so

class XkcdComicModel(db_lib.Base):
    """Table model for XKCD comics.

    Params:
        year (str): Published year
        month (str): Published month
        day (str): Published day
        comic_num (int): Comic number
        link (str|None): Link to comic.
        title (str): Comic title.
        transcript (str|None): Comic transcript.
        alt_text (str): Comic alt text.
        img_url (str): Link to comic image.
        img (bytes): Image bytestring.

    """

    __tablename__ = "xkcd_comic"
    __table_args__ = (sa.UniqueConstraint("num", name="_comic_num_uc"),)

    id: so.Mapped[db_lib.annotated.INT_PK]

    year: so.Mapped[str] = so.mapped_column(sa.TEXT)
    month: so.Mapped[str] = so.mapped_column(sa.TEXT)
    day: so.Mapped[str] = so.mapped_column(sa.TEXT)
    num: so.Mapped[int] = so.mapped_column(sa.INTEGER)
    link: so.Mapped[str | None] = so.mapped_column(sa.TEXT)
    title: so.Mapped[str] = so.mapped_column(sa.TEXT)
    transcript: so.Mapped[str | None] = so.mapped_column(sa.TEXT)
    alt_text: so.Mapped[str] = so.mapped_column(__name_pos=sa.TEXT)
    img_url: so.Mapped[str] = so.mapped_column(sa.TEXT)
    img_saved: so.Mapped[bool] = so.mapped_column(sa.BOOLEAN, default=False)
    comic_num_hash: so.Mapped[str] = so.mapped_column(sa.TEXT)


class XkcdCurrentComicMetadataModel(db_lib.Base):
    __tablename__ = "current_comic_meta"
    __table_args__ = (sa.UniqueConstraint("num", name="_current_comic_num_uc"),)

    id: so.Mapped[db_lib.annotated.INT_PK]

    num: so.Mapped[int] = so.mapped_column(sa.INTEGER)
    last_updated: so.Mapped[datetime] = so.mapped_column(sa.DateTime)


class XkcdComicImageModel(db_lib.Base):
    __tablename__ = "comic_img"
    __table_args__ = (sa.UniqueConstraint("num", name="_comic_img_num_uc"),)

    id: so.Mapped[db_lib.annotated.INT_PK]

    num: so.Mapped[int] = so.mapped_column(sa.INTEGER)
    img_bytes: so.Mapped[bytes] = so.mapped_column(sa.LargeBinary)

    def __repr__(self):
        return f"XkcdComicImageModel(id={self.id or None}, num={self.num})"
