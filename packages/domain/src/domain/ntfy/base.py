from __future__ import annotations

import logging
import typing as t

from pydantic import BaseModel, Field, ValidationError, computed_field, field_validator


class BaseAction(BaseModel):
    label: str
    url: str
    actions: list
    clear: bool = Field(default=False)
