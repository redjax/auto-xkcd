from __future__ import annotations

VALID_COL_TYPES: list[str] = [
    "object",
    "bool",
    "category",
    "complex128",
    "uint8",
    "uint16",
    "uint32",
    "uint64",
    "int8",
    "int16",
    "int32",
    "int64",
    "float16",
    "float32",
    "float64",
    "datetime64[ns]",
    "datetime64[tz]",
    "timedelta[ns]",
]


def validate_df_col_type(col_type: str = None) -> str:
    """Validate a given column type is in the list of allowed column types.

    Params:
        col_type (str): The `pandas`/`numpy` datatype of a column.

    Returns:
        (str): The validated `col_type`

    Raises:
        ValueError: If a `col_type` does not exist in the list of `VALID_COL_TYPES`, a `ValueError` is raised

    """
    if col_type is None:
        raise ValueError("Missing a column type to validate")

    if col_type in VALID_COL_TYPES:
        return col_type
    else:
        raise ValueError(
            f"Invalid column type: [{col_type}]. Must be one of {VALID_COL_TYPES}"
        )