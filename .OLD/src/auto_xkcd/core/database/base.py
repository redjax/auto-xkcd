"""Define the SQLAlchemy `DeclarativeBase` object."""

from __future__ import annotations

import sqlalchemy as sa
import sqlalchemy.orm as so

REGISTRY: so.registry = so.registry()
METADATA: sa.MetaData = sa.MetaData()


class Base(so.DeclarativeBase):
    """Initialize a SQLAlchemy `DeclarativeBase` instance.

    Params:
        registry (sqalchemy.orm.registry): <Not documented>
        metadata (sqlalchemy.MetaData): <Not documented>

    """

    registry: so.registry = REGISTRY
    metadata: sa.MetaData = METADATA
