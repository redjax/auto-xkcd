from loguru import logger as log

from datetime import datetime
import db_lib

import sqlalchemy as sa
import sqlalchemy.orm as so
import sqlalchemy.exc as sa_exc


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

    year: so.Mapped[str] = so.mapped_column(sa.VARCHAR(255))
    month: so.Mapped[str] = so.mapped_column(sa.VARCHAR(255))
    day: so.Mapped[str] = so.mapped_column(sa.VARCHAR(255))
    num: so.Mapped[int] = so.mapped_column(sa.INTEGER)
    link: so.Mapped[str | None] = so.mapped_column(sa.VARCHAR(255))
    title: so.Mapped[str] = so.mapped_column(sa.VARCHAR(255))
    transcript: so.Mapped[str | None] = so.mapped_column(sa.VARCHAR(255))
    alt_text: so.Mapped[str] = so.mapped_column(__name_pos=sa.VARCHAR(255))
    img_url: so.Mapped[str] = so.mapped_column(sa.VARCHAR(255))
    img_saved: so.Mapped[bool] = so.mapped_column(sa.BOOLEAN, default=False)
    comic_num_hash: so.Mapped[str] = so.mapped_column(sa.VARCHAR(255))


class XkcdCurrentComicMetadataModel(db_lib.Base):
    __tablename__ = "current_comic_meta"
    __table_args__ = (sa.UniqueConstraint("num", name="_comic_num_uc"),)

    id: so.Mapped[db_lib.annotated.INT_PK]

    num: so.Mapped[int] = so.mapped_column(sa.INTEGER)
    last_updated: so.Mapped[datetime] = so.mapped_column(sa.DateTime)
    
    
class XkcdComicImageModel(db_lib.Base):
    __tablename__ = "comic_img"
    __table_args__ = (sa.UniqueConstraint("num", name="_comic_num_uc"),)

    id: so.Mapped[db_lib.annotated.INT_PK]

    num: so.Mapped[int] = so.mapped_column(sa.INTEGER)
    img_bytes: so.Mapped[bytes] = so.mapped_column(sa.LargeBinary)
    
    def __repr__(self):
        return f"XkcdComicImageModel(id={self.id or None}, num={self.num})"
