import typing as t
from pathlib import Path

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    ValidationError,
    computed_field,
    ConfigDict,
)

from utils.path_utils import get_dir_size

from loguru import logger as log


class DirSizeResponse(BaseModel):
    dir_path: t.Union[str, Path] = Field(default=None)

    @field_validator("dir_path")
    def validate_dir_path(cls, v) -> Path:
        if not isinstance(v, str) and not isinstance(v, Path):
            # raise TypeError(f"Invalid type for dir_path, must be a string or Path. Got type: ({type(v)})")
            raise ValidationError

        v: Path = Path(f"{v}")

        return v

    @property
    def dir_name(self) -> str:
        return self.dir_path.name

    @property
    def size_in_bytes(self) -> int:
        return get_dir_size(self.dir_path)[0]

    @property
    def size_str(self) -> int:
        return get_dir_size(self.dir_path)[1]
