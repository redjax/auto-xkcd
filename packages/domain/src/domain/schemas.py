import datetime as dt
import typing as t

from loguru import logger as log

from pydantic import BaseModel, Field, field_validator, ValidationError, ConfigDict

