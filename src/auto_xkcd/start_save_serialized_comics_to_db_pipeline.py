from core import database
from _setup import base_app_setup
from core.dependencies import db_settings
from pipelines import data_pipelines

from loguru import logger as log

if __name__ == "__main__":
    base_app_setup()

    try:
        database.create_base_metadata(
            base=database.Base, engine=db_settings.get_engine()
        )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception creating SQLAlchemy Base metadata. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        log.warning(
            f"Continuing without initializing database. This will probably cause issues."
        )

    try:
        data_pipelines.pipeline_save_serialized_comics_to_db()
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception running pipeline to save serialized XKCDComic objects to database. Details: {exc}"
        )
        log.error(msg)
        log.trace(exc)

        raise exc
