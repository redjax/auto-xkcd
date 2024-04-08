from __future__ import annotations

import abc
from datetime import date

from core.database import INT_PK, Base, TableNameMixin, TimestampMixin
import sqlalchemy as sa
import sqlalchemy.orm as so

class XKCDComicModel(Base):
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
    img: so.Mapped[bytes] = so.mapped_column(sa.LargeBinary)


class XKCDComicRepositoryBase(metaclass=abc.ABCMeta):
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


class XKCDSentComicModel(Base):
    __tablename__ = "xkcd_sent_comic"
    __table_args__ = (sa.UniqueConstraint("comic_num", name="_comic_num_uc"),)

    sent_comic_id: so.Mapped[INT_PK]
    comic_num: so.Mapped[int] = so.mapped_column(sa.INTEGER)
    date_sent: so.Mapped[date] = so.mapped_column(sa.Date)


class XKCDSentComicRepositoryBase(metaclass=abc.ABCMeta):
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
