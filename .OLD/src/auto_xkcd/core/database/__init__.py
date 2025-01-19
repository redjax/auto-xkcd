"""The database module is the basis for database operations.

The SQLAlchemy `DeclarativeBase` object is defined here, and methods for
creating base metadata, getting a database engine, etc are defined here.

This module also has useful mixins/addons for SQLAlchemy, like annotated columns
for an `INT_PK`, or a `VARCHAR(10)` column type defined in `STR_10`.

Mixin classes for SQLAlchemy model classes, like `TimestampMixin`, automatically
add columns & values to models stored in the database.
"""

from __future__ import annotations

from .annotated import INT_PK, STR_10, STR_255
from .base import Base
from .db_config import DBSettings
from .methods import create_base_metadata, get_db_uri, get_engine, get_session_pool
from .mixins import TableNameMixin, TimestampMixin
