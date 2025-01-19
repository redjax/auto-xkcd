from __future__ import annotations

from pathlib import Path

import db_lib as db
from depends import db_depends
from loguru import logger as log
import sqlalchemy as sa
import sqlalchemy.orm as so

def setup_database(sqla_base: so.DeclarativeBase = db.Base,engine: sa.Engine = db_depends.get_db_engine()) -> None:
    """Setup the database tables and metadata.
    
    Params:
        sqla_base (sqlalchemy.orm.DeclarativeBase): A SQLAlchemy `DeclarativeBase` object to use for creating metadata.
        engine (sqlalchemy.Engine): A SQLAlchemy `Engine` to use for database connections.
    """
    engine: sa.Engine = engine
    
    ## Check if the driver is SQLite
    if engine.dialect.name == 'sqlite':
        ## Get the database file path from the engine's URL
        db_file_path = engine.url.database
        
        ## Get the parent directory of the database file
        parent_dir = Path(db_file_path).parent
        
        ## Check if the parent directory exists
        if not parent_dir.exists():
            ## Create the parent directory if it doesn't exist
            try:
                parent_dir.mkdir(parents=True, exist_ok=True)
            except Exception as exc:
                msg = f"({type(exc)}) Detected SQLite database, but could not create at path: {parent_dir}. Details: {exc}"
                log.error(msg)
                raise exc

    db.create_base_metadata(base=sqla_base, engine=engine)
