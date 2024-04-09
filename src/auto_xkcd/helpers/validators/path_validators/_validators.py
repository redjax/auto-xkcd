from __future__ import annotations

from pathlib import Path
import typing as t


def validate_path(p: t.Union[str, Path] = None, must_exist: bool = False) -> Path:
    """Validate an input path.

    Params:
        p (str|Path): A path to a file or directory.
        must_exist (bool): If `True`, raise `FileNotFoundError` if `p` does not exist.

    Returns:
        (Path): A validated `Path` object.

    """
    assert p, ValueError("Path cannot be none")
    assert isinstance(p, str) or isinstance(p, Path), TypeError(
        f"Path must be a string or Path. Got type: ({type(p)})"
    )
    if isinstance(p, str):
        p: Path = Path(p)
    if "~" in f"{p}":
        p: Path = p.expanduser()

    return p
