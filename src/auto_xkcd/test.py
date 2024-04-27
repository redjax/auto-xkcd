from __future__ import annotations

from core.config import settings, db_settings
from core import database
from core.dependencies import get_db
from domain.xkcd import comic

from loguru import logger as log

if __name__ == "__main__":

    log.debug(f"DB settings: {db_settings}")

    delete_ids = [1, 2]
    with get_db() as session:
        repo = comic.CurrentComicMetaRepository(session=session)

        try:
            ex = repo.get_by_num(2922)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception getting current comic metadata. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            raise msg

        for _id in delete_ids:
            log.info(f"Deleting comic meta with ID '{_id}'")
            try:
                _entity = repo.get_by_id(_id)
                if _entity is None:
                    log.warning(f"Did not find current comic metadata with ID '{_id}'.")
                    continue
            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception getting entity by ID '{_id}'. Details: {exc}"
                )
                log.error(msg)
                log.trace(exc)

                raise exc

            if _entity:

                try:
                    repo.remove(_entity)
                except Exception as exc:
                    msg = Exception(
                        f"Unhandled exception deleting entity with ID '{_id}'. Details: {exc}"
                    )
                    log.error(msg)
                    log.trace(exc)

                    raise exc

            session.commit()
