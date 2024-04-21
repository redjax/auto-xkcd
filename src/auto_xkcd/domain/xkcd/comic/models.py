"""SQLAlchemy table classes for XKCD comics."""

from __future__ import annotations

import abc
from datetime import date, datetime

from core.database import INT_PK, Base, TableNameMixin, TimestampMixin
import sqlalchemy as sa
import sqlalchemy.orm as so


class XKCDComicModel(Base):
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
    __table_args__ = (sa.UniqueConstraint("comic_num", name="_comic_num_uc"),)

    comic_id: so.Mapped[INT_PK]

    year: so.Mapped[str] = so.mapped_column(sa.VARCHAR(255))
    month: so.Mapped[str] = so.mapped_column(sa.VARCHAR(255))
    day: so.Mapped[str] = so.mapped_column(sa.VARCHAR(255))
    comic_num: so.Mapped[int] = so.mapped_column(sa.INTEGER)
    link: so.Mapped[str | None] = so.mapped_column(sa.VARCHAR(255))
    title: so.Mapped[str] = so.mapped_column(sa.VARCHAR(255))
    transcript: so.Mapped[str | None] = so.mapped_column(sa.VARCHAR(255))
    alt_text: so.Mapped[str] = so.mapped_column(__name_pos=sa.VARCHAR(255))
    img_url: so.Mapped[str] = so.mapped_column(sa.VARCHAR(255))
    img_saved: so.Mapped[bool] = so.mapped_column(sa.BOOLEAN, default=False)
    # img: so.Mapped[bytes] = so.mapped_column(sa.LargeBinary)
    comic_num_hash: so.Mapped[str] = so.mapped_column(sa.VARCHAR(255))


class XKCDComicRepositoryBase(metaclass=abc.ABCMeta):
    """Base database repository class for XKCDComic."""

    @abc.abstractmethod
    def add(self, entity: XKCDComicModel):
        """Add new entity to repository."""
        raise NotImplementedError()

    @abc.abstractmethod
    def remove(self, entity: XKCDComicModel):
        """Remove existing entity from repository."""
        raise NotImplementedError()

    @abc.abstractmethod
    def get_by_id(self, comic_id: int) -> XKCDComicModel:
        """Retrieve entity from repository by its ID."""
        raise NotImplementedError()


class CurrentComicMetaModel(Base):
    __tablename__ = "xkcd_current_comic_meta"
    __table_args__ = (sa.UniqueConstraint("comic_num", name="_comic_num_uc"),)

    current_comic_id: so.Mapped[INT_PK]

    comic_num: so.Mapped[int] = so.mapped_column(sa.INTEGER)
    last_updated: so.Mapped[datetime] = so.mapped_column(sa.DateTime)


class CurrentComicMetaRepositoryBase(metaclass=abc.ABCMeta):
    """Base database repository class for XKCDCurrentComicMeta."""

    @abc.abstractmethod
    def add(self, entity: CurrentComicMetaModel):
        """Add new entity to repository."""
        raise NotImplementedError()

    @abc.abstractmethod
    def remove(self, entity: CurrentComicMetaModel):
        """Remove existing entity from repository."""
        raise NotImplementedError()

    @abc.abstractmethod
    def get_by_id(self, comic_id: int) -> CurrentComicMetaModel:
        """Retrieve entity from repository by its ID."""
        raise NotImplementedError()


class XKCDComicImageModel(Base):
    __tablename__ = "xkcd_comic_img"
    __table_args__ = (sa.UniqueConstraint("comic_num", name="_comic_num_uc"),)

    comic_img_id: so.Mapped[INT_PK]

    comic_num: so.Mapped[int] = so.mapped_column(sa.INTEGER)
    img: so.Mapped[bytes] = so.mapped_column(sa.LargeBinary)


class XKCDComicImageRepositoryBase(metaclass=abc.ABCMeta):
    """Base database repository for XKCDComicImage."""

    @abc.abstractmethod
    def add(self, entity: XKCDComicImageModel):
        """Add new entity to repository."""
        raise NotImplementedError()

    @abc.abstractmethod
    def remove(self, entity: XKCDComicImageModel):
        """Remove existing entity from repository."""
        raise NotImplementedError()

    @abc.abstractmethod
    def get_by_id(self, comic_id: int) -> XKCDComicImageModel:
        """Retrieve entity from repository by its ID."""
        raise NotImplementedError()


class XKCDSentComicModel(Base):
    """Metadata about comics sent via Telegram.

    Params:
        sent_comic_id (INT_PK): Primary key for sent comic.
        comic_num (int): Comic's number.
        date_sent (date): Day the comic was sent on Telegram.
    """

    __tablename__ = "xkcd_sent_comic"
    __table_args__ = (sa.UniqueConstraint("comic_num", name="_comic_num_uc"),)

    sent_comic_id: so.Mapped[INT_PK]
    comic_num: so.Mapped[int] = so.mapped_column(sa.INTEGER)
    date_sent: so.Mapped[date] = so.mapped_column(sa.Date)


class XKCDSentComicRepositoryBase(metaclass=abc.ABCMeta):
    """Base database repository for XKCDSentComic."""

    @abc.abstractmethod
    def add(self, entity: XKCDSentComicModel):
        """Add new entity to repository."""
        raise NotImplementedError()

    @abc.abstractmethod
    def remove(self, entity: XKCDSentComicModel):
        """Remove existing entity from repository."""
        raise NotImplementedError()

    @abc.abstractmethod
    def get_by_id(self, comic_id: int) -> XKCDSentComicModel:
        """Retrieve entity from repository by its ID."""
        raise NotImplementedError()
