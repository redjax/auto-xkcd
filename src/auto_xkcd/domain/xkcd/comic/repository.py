from __future__ import annotations

from .models import (
    XKCDComicModel,
    XKCDComicRepositoryBase,
    XKCDSentComicModel,
    XKCDSentComicRepositoryBase,
)

from loguru import logger as log
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
import sqlalchemy.orm as so


class XKCDComicRepository(XKCDComicRepositoryBase):
    """Database repository for handling XKCDComic entities."""

    def __init__(self, session: so.Session) -> None:  # noqa: D107
        assert session is not None, ValueError("session cannot be None")
        assert isinstance(session, so.Session), TypeError(
            f"session must be of type sqlalchemy.orm.Session. Got type: ({type(session)})"
        )

        self.session: so.Session = session

    def add(self, entity: XKCDComicModel) -> None:
        """Add new entity to the database."""
        try:
            self.session.add(instance=entity)
            self.session.commit()
        except IntegrityError as integ:
            msg = Exception(
                f"Integrity error committing entity to database. Details: {integ}"
            )
            log.warning(msg)

            raise integ
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception committing entity to database. Details: {exc}"
            )

            raise msg

    def remove(self, entity: XKCDComicModel) -> None:
        """Remove existing entity from the database."""
        try:
            self.session.delete(instance=entity)
            self.session.commit()
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception removing entity from database. Details: {exc}"
            )
            log.error(msg)

            raise msg

    def get_all_comic_nums(self) -> list[int]:
        """Return a list of all comic numbers in database entitites."""
        try:
            all_comics: list[XKCDComicModel] = self.session.query(XKCDComicModel).all()
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception getting all comic numbers from database. Details: {exc}"
            )
            log.error(msg)

            raise msg

        _nums: list[int] = []

        for _comic in all_comics:
            _nums.append(_comic.num)

        return _nums

    def get_all(self) -> list[XKCDComicModel]:
        """Return a list of all entitites found in database."""
        try:
            all_comics: list[XKCDComicModel] = self.session.query(XKCDComicModel).all()

            return all_comics
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception getting all comic numbers from database. Details: {exc}"
            )
            log.error(msg)

            raise msg

    def get_by_id(self, comic_id: int) -> XKCDComicModel:
        try:
            return self.session.query(XKCDComicModel).get(comic_id)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception retrieving entity by ID '{comic_id}'. Details: {exc}"
            )
            log.error(msg)

            raise msg


class XKCDSentComicRepository(XKCDSentComicRepositoryBase):
    """Database repository for handling XKCDSentComic models."""

    def __init__(self, session: so.Session) -> None:  # noqa: D107
        assert session is not None, ValueError("session cannot be None")
        assert isinstance(session, so.Session), TypeError(
            f"session must be of type sqlalchemy.orm.Session. Got type: ({type(session)})"
        )

        self.session: so.Session = session

    def add(self, entity: XKCDSentComicModel) -> None:
        try:
            self.session.add(instance=entity)
            self.session.commit()
        except IntegrityError as integ:
            msg = Exception(
                f"Integrity error committing entity to database. Details: {integ}"
            )
            log.warning(msg)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception committing entity to database. Details: {exc}"
            )

            raise msg

    def remove(self, entity: XKCDSentComicModel) -> None:
        try:
            self.session.delete(instance=entity)
            self.session.commit()
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception removing entity from database. Details: {exc}"
            )
            log.error(msg)

            raise msg

    def get_all_sent_comic_nums(self) -> list[int]:
        """Return a list of all sent comic numbers in database entitites."""
        try:
            all_sent_comics: list[XKCDSentComicModel] = self.session.query(
                XKCDSentComicModel
            ).all()
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception getting all sent comic numbers from database. Details: {exc}"
            )
            log.error(msg)

            raise msg

        _nums: list[int] = []

        for _comic in all_sent_comics:
            _nums.append(_comic.num)

        return _nums

    def get_all(self) -> list[XKCDSentComicModel]:
        """Return a list of all entitites found in database."""
        try:
            all_comics: list[XKCDSentComicModel] = self.session.query(
                XKCDSentComicModel
            ).all()

            return all_comics
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception getting all comic numbers from database. Details: {exc}"
            )
            log.error(msg)

            raise msg

    def get_by_id(self, sent_comic_id: int) -> XKCDSentComicModel:
        """Get an entity from the database by ID."""
        try:
            return self.session.query(XKCDSentComicModel).get(sent_comic_id)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception retrieving entity by ID '{sent_comic_id}'. Details: {exc}"
            )
            log.error(msg)

            raise msg
