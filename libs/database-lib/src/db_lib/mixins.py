"""SQLAlchemy models support multi-inheritance.

"Mixins" ([SQLAlchemy declarative mixins docs](https://docs.sqlalchemy.org/en/20/orm/declarative_mixins.html)) are partial classes
that predefine some attributes and methods. These can enhance SQLAlchemy table classes you create (model classes that inherit from your `Base`),
like adding a "modified" timestamp, or automatically naaming tables based on the model class's name.
"""

from __future__ import annotations

from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as so

class TimestampMixin:
    """Add a created_at & updated_at column to records.

    Add to class declaration to automatically create these columns on
    records.

    Usage:

    ``` py linenums=1
    class Record(Base, TimestampMixin):
        __tablename__ = ...

        ...
    ```
    """

    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.TIMESTAMP, server_default=sa.func.now()
    )
    updated_at: so.Mapped[datetime] = so.mapped_column(
        sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now()
    )


class TableNameMixin:
    """Mixin to automatically name tables based on class name.

    Generates a `__tablename__` for classes inheriting from this mixin.
    """

    @so.declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: D105
        return cls.__name__.lower() + "s"
