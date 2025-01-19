from __future__ import annotations

import logging
from pathlib import Path
import typing as t

import pandas as pd

log = logging.getLogger(__name__)


def hide_df_index(df: pd.DataFrame) -> pd.DataFrame:
    """Hide the Pandas index when previewing, i.e. with .head().
    
    Params:
        df (pandas.DataFrame): A Pandas `DataFrame` to hide the index.
        
    Returns:
        (pandas.DataFrame): A Pandas `DataFrame` with the index hidden

    """
    ## Create index of empty strings for each row in the dataframe
    blank_index=[''] * len(df)
    ## Set the dataframe's index to the list of empty strings
    df.index = blank_index
    
    return df


def set_pandas_display_opts(
    max_rows: int | None = 60,
    max_columns: int | None = 20,
    max_colwidth: int | None = 50,
    max_width: int | None = None
) -> None:
    """Set Pandas display options.

    Params:
        max_rows (int|None): Max number of rows to show in a dataframe. None=infinite
        max_columns (int|None): Max number of columns to show in a dataframe. Truncated columns appear as: |...|. None=infinite
        max_colwidth (int|None): Number of characters before truncating text. None=infinite
        max_width (int|None): Maximum width of the entire console display in characters. If None, Pandas adjusts display automatically.
    """
    log.debug(f"""Pandas options:
max_rows: {max_rows}
max_columns: {max_columns}
max_colwidth: {max_colwidth}
max_width: {max_width}
""")
    pd.set_option("display.max_rows", max_rows)
    pd.set_option("display.max_columns", max_columns)
    pd.set_option("display.max_colwidth", max_colwidth)
    pd.set_option("display.width", max_width)


def rename_df_cols(
    df: pd.DataFrame = None, col_rename_map: dict[str, str] = None
) -> pd.DataFrame:
    """Return a DataFrame with columns renamed based on input col_rename_map.

    Params:
        df (pandas.DataFrame): A Pandas `DataFrame` with columns to rename
            col_rename_map (dict[str, str]): A Python `dict` defining existing column names and the value
            they should be renamed to.

    Returns:
        (pandas.DataFrame): A renamed Pandas `DataFrame`.

    """
    if col_rename_map is None:
        msg = ValueError("No col_rename_map passed")
        log.warning(msg)

        return df

    if df is None or df.empty:
        msg = ValueError("Missing DataFrame, or DataFrame is empty")
        log.error(msg)

        raise ValueError(msg)

    try:
        df = df.rename(columns=col_rename_map)

        return df
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception renaming DataFrame columns. Details: {exc}"
        )
        log.error(msg)

        raise exc


def count_df_rows(df: pd.DataFrame = None) -> int:
    """Return count of the number of rows in a DataFrame.

    Params:
        df (pandas.DataFrame): A Pandas `DataFrame` to count the rows in

    Returns:
        (int): Count of rows in a `DataFrame`

    """
    if df is not None:
        if df.empty:
            return
    else:
        return

    if not isinstance(df, pd.DataFrame) and not isinstance(df, pd.Series):
        raise TypeError(
            f"Invalid type for DataFrame: ({type(df)}). Must be a Pandas Series or DataFrame"
        )

    return len(df.index)


def load_pqs_to_df(
    search_dir: str = None, filetype: str = ".parquet"
) -> list[pd.DataFrame]:
    """Load data export files in search_dir into list of DataFrames.

    Params:
        search_dir (str): The directory to search for files in
        filetype (str): The file extension to filter results by

    Returns:
        (list[pandas.DataFrame]): A list of Pandas `DataFrame`s created from files in `search_dir`

    """
    if search_dir is None:
        raise ValueError("Missing a directory to search")

    if not filetype.startswith("."):
        filetype = f".{filetype}"

    files: list[Path] = []

    for f in Path(search_dir).glob(f"**/*{filetype}"):
        if f.is_file():
            files.append(f)

    dataframes: list[pd.DataFrame] = []

    if filetype == ".parquet":
        for pq in files:
            df = load_pq(pq_file=pq)

            dataframes.append(df)

    elif filetype == ".csv":
        for f in files:
            df = pd.read_csv(f)

            dataframes.append(df)

    return dataframes


def convert_csv_to_pq(
    csv_file: t.Union[str, Path] = None,
    pq_file: t.Union[str, Path] = None,
    dedupe: bool = False,
) -> bool:
    """Read a CSV file into a DataFrame, then write the DataFrame to a Parquet file.

    Params:
        csv_file (str|Path): Path to a CSV file to read from
        pq_file (str|Path): Path to a Parquet file to write to
        dedupe (bool): Whether to run .drop_duplicates() on the DataFrame

    Returns:
        (bool): `True` if `csv_file` is converted to `pq_file` successfully

    Raises:
        Exception: If file cannot be saved, an `Exception` is raised instead of returning
            a bool value

    """
    if csv_file is None:
        raise ValueError("Missing a CSV input file to read from")
    if pq_file is None:
        raise ValueError("Missing a Parquet file to save to")

    if isinstance(csv_file, str):
        csv_file: Path = Path(csv_file)
    if isinstance(pq_file, str):
        pq_file: Path = Path(pq_file)

    if not csv_file.exists():
        raise FileNotFoundError(f"Could not find input CSV file at path: {csv_file}")

    try:
        df = load_csv(csv_file=csv_file)
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception reading CSV file '{csv_file}' to DataFrame. Details: {exc}"
        )
        log.error(msg)

        raise exc

    try:
        success = save_pq(df=df, pq_file=pq_file, dedupe=dedupe)

        return success

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception writing DataFrame to file: {pq_file}. Details: {exc}"
        )
        log.error(msg)

        raise exc


def convert_pq_to_csv(
    pq_file: t.Union[str, Path] = None,
    csv_file: t.Union[str, Path] = None,
    dedupe: bool = False,
) -> bool:
    """Read a Parquet file into a DataFrame, then write the DataFrame to a CSV file.

    Params:
        pq_file (str|Path): Path to a Parquet file to read from
        csv_file (str|Path): Path to a CSV file to write to
        dedupe (bool): Whether to run .drop_duplicates() on the DataFrame

    Returns:
        (bool): `True` if `pq_file` is converted to `csv_file` successfully

    Raises:
        Exception: If file cannot be saved, an `Exception` is raised instead of returning
            a bool value

    """
    if csv_file is None:
        raise ValueError("Missing a CSV file to save to")
    if pq_file is None:
        raise ValueError("Missing an input Parquet file to read from")

    if isinstance(csv_file, str):
        csv_file: Path = Path(csv_file)
    if isinstance(pq_file, str):
        pq_file: Path = Path(pq_file)

    if not pq_file.exists():
        raise FileNotFoundError(f"Could not find input Parquet file at path: {pq_file}")

    try:
        df = load_pq(pq_file=pq_file)
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception reading Parquet file '{pq_file}' to DataFrame. Details: {exc}"
        )
        log.error(msg)

        raise exc

    try:
        success = save_csv(df=df, csv_file=csv_file, columns=df.columns, dedupe=dedupe)

        return success

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception writing DataFrame to file: {csv_file}. Details: {exc}"
        )
        log.error(msg)

        raise exc


def load_pq(
    pq_file: t.Union[str, Path] = None, pq_engine: str = "pyarrow"
) -> pd.DataFrame:
    """Return a DataFrame from a previously saved .parquet file.

    Params:
        pq_file (str|Path): Path to a `.parquet` file to load

    Returns:
        (pandas.DataFrame): A Pandas `DataFrame` loaded from a `.parquet` file

    """
    if pq_file is None:
        raise ValueError("Missing pq_file to load")
    if isinstance(pq_file, str):
        pq_file: Path = Path(pq_file)

    if not pq_file.suffix == ".parquet":
        pq_file: Path = Path(f"{pq_file}.parquet")

    if not pq_file.exists():
        msg = FileNotFoundError(f"Could not find Parquet file at '{pq_file}'")
        # log.error(msg)
        log.error(msg)

        raise exc

    try:
        df = pd.read_parquet(pq_file, engine=pq_engine)

        return df

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception loading Parquet file '{pq_file}' to DataFrame. Details: {exc}"
        )
        log.error(msg)

        raise exc


def save_pq(
    df: pd.DataFrame = None,
    pq_file: t.Union[str, Path] = None,
    dedupe: bool = False,
    pq_engine: str = "pyarrow",
) -> bool:
    """Save DataFrame to a .parquet file.

    Params:
        df (pandas.DataFrame): A Pandas `DataFrame` to save
        pq_file (str|Path): The path to a `.parquet` file where the `DataFrame` should be saved
        dedupe (bool): If `True`, deduplicate the `DataFrame` before saving

    Returns:
        (bool): `True` if `DataFrame` is saved to `pq_file` successfully
        (bool): `False` if `DataFrame` is not saved to `pq_file` successfully

    Raises:
        Exception: If file cannot be saved, an `Exception` is raised

    """
    if df is None or df.empty:
        msg = ValueError("DataFrame is None or empty")
        log.warning(msg)

        return False

    if pq_file is None:
        raise ValueError("Missing output path")
    if isinstance(pq_file, str):
        pq_file: Path = Path(pq_file)

    if pq_file.suffix != ".parquet":
        new_str = str(f"{pq_file}.parquet")
        pq_file: Path = Path(new_str)

    if not pq_file.parent.exists():
        try:
            pq_file.parent.mkdir(exist_ok=True, parents=True)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception creating directory: {pq_file.parent}. Details: {exc}"
            )
            log.error(msg)

            return False

    try:
        if dedupe:
            df = df.drop_duplicates()

        output = df.to_parquet(path=pq_file, engine=pq_engine)

        return True

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception saving DataFrame to Parquet file: {pq_file}. Details: {exc}"
        )
        log.error(msg)
        raise exc


def load_csv(csv_file: t.Union[str, Path] = None, delimiter: str = ",") -> pd.DataFrame:
    """Load a CSV file into a DataFrame.

    Params:
        csv_file (str|Path): The path to a `.csv` file to load into a `DataFrame
        delimiter (str): The delimiter symbol the `csv_file` uses

    Returns:
        (pandas.DataFrame): A Pandas `DataFrame` with data loaded from the `csv_file`

    """
    if csv_file is None:
        raise ValueError("Missing output path")

    if isinstance(csv_file, str):
        csv_file: Path = Path(csv_file)

    if csv_file.suffix != ".csv":
        new_str = str(f"{csv_file}.csv")
        csv_file: Path = Path(new_str)

    if not csv_file.exists():
        msg = FileNotFoundError(f"Could not find CSV file: '{csv_file}'.")
        log.error(msg)
        raise exc

    try:
        df = pd.read_csv(csv_file, delimiter=delimiter)

        return df

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception loading DataFrame from CSV file: {csv_file}. Details: {exc}"
        )
        log.error(msg)

        raise exc


def save_csv(
    df: pd.DataFrame = None,
    csv_file: t.Union[str, Path] = None,
    columns: list[str] = None,
    dedupe: bool = False,
) -> bool:
    """Save DataFrame to a .csv file.

    Params:
        df (pandas.DataFrame): A Pandas `DataFrame` to save
        csv_file (str|Path): The path to a `.csv` file where the `DataFrame` should be saved
        columns (list[str]): A list of string values representing column names for the `.csv` file
        dedupe (bool): If `True`, deduplicate the `DataFrame` before saving

    Returns:
        (bool): `True` if `DataFrame` is saved to `csv_file` successfully
        (bool): `False` if `DataFrame` is not saved to `csv_file` successfully

    Raises:
        Exception: If file cannot be saved, an `Exception` is raised

    """
    if df is None or df.empty:
        msg = ValueError("DataFrame is None or empty")

        return False

    if csv_file is None:
        raise ValueError("Missing output path")
    if isinstance(csv_file, str):
        csv_file: Path = Path(csv_file)

    if csv_file.suffix != ".csv":
        new_str = str(f"{csv_file}.csv")
        csv_file: Path = Path(new_str)

    if not csv_file.parent.exists():
        try:
            csv_file.parent.mkdir(exist_ok=True, parents=True)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception creating directory: {csv_file.parent}. Details: {exc}"
            )
            log.error(msg)

            return False

    if columns is None:
        columns = df.columns

    try:
        if dedupe:
            df = df.drop_duplicates()

        if columns is not None:
            output = df.to_csv(csv_file, columns=columns)
        else:
            output = df.to_csv(csv_file)

        return True

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception saving DataFrame to Parquet file: {csv_file}. Details: {exc}"
        )
        log.error(msg)
        raise exc
    

def save_json(df: pd.DataFrame = None, json_file: t.Union[str, Path] = None, indent: int | None = None) -> bool:
    """Save DataFrame to a .json file.

    Params:
        df (pandas.DataFrame): A Pandas `DataFrame` to save
        json_file (str|Path): The path to a `.json` file where the `DataFrame` should be saved

    Returns:
        (bool): `True` if `DataFrame` is saved to `json_file` successfully
        (bool): `False` if `DataFrame` is not saved to `json_file` successfully

    Raises:
        Exception: If file cannot be saved, an `Exception` is raised

    """
    if df is None or df.empty:
        msg = ValueError("DataFrame is None or empty")
        log.warning(msg)

        return False

    if json_file is None:
        raise ValueError("Missing output path")
    if isinstance(json_file, str):
        json_file: Path = Path(json_file)

    if json_file.suffix != ".json":
        new_str = str(f"{json_file}.json")
        json_file: Path = Path(new_str)

    if not json_file.parent.exists():
        try:
            json_file.parent.mkdir(exist_ok=True, parents=True)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception creating directory: {json_file.parent}. Details: {exc}"
            )
            log.error(msg)

            return False

    try:
        df.to_json(json_file, orient="records", indent=indent)
        return True

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception saving DataFrame to JSON file: {json_file}. Details: {exc}"
        )
        log.error(msg)
        raise exc


def load_json(json_file: t.Union[str, Path] = None) -> pd.DataFrame:
    """Load a JSON file into a DataFrame.

    Params:
        json_file (str|Path): The path to a `.json` file to load into a `DataFrame`

    Returns:
        (pandas.DataFrame): A Pandas `DataFrame` loaded from the `json_file`

    Raises:
        Exception: If file cannot be loaded, an `Exception` is raised

    """
    if json_file is None:
        raise ValueError("Missing input file to load")

    if isinstance(json_file, str):
        json_file: Path = Path(json_file)

    if not json_file.exists():
        msg = FileNotFoundError(f"Could not find JSON file at '{json_file}'")
        log.error(msg)
        raise exc

    try:
        df = pd.read_json(json_file, orient="records")
        return df

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception loading JSON file '{json_file}' to DataFrame. Details: {exc}"
        )
        log.error(msg)
        raise exc


def sort_df_by_col(df: pd.DataFrame, col_name: str, order: str = "asc") -> pd.DataFrame:
    """Sorts a Pandas DataFrame by a specified column in ascending or descending order.

    Params:
        df (pd.DataFrame): The DataFrame to sort.
        col_name (str): The column name to sort by.
        order (str): The sorting order, "asc" for ascending (default) or "desc" for descending.

    Returns:
        pd.DataFrame: The sorted DataFrame.

    """
    if col_name not in df.columns:
        raise ValueError(f"Column '{col_name}' not found in DataFrame.")
    if order not in ["asc", "desc"]:
        raise ValueError("Order must be 'asc' or 'desc'.")

    ## Set ascending=True if order="asc" else False
    ascending = order == "asc"

    return df.sort_values(by=col_name, ascending=ascending)


def get_oldest_newest(
    df: pd.DataFrame = None, date_col: str = None, filter_cols: list[str] | None = None
) -> t.Union[pd.Series, pd.DataFrame]:
    """Get the oldest and newest rows in a DataFrame.

    Params:
        df (pd.DataFrame): Pandas DataFrame to work on
        date_col (str): Name of the column to sort by
        filter_cols (list[str]): List of column names to return with the oldest/newest record.

    Returns:
        (pandas.Series|pandas.DataFrame): A Pandas `DataFrame` or `Series` containing oldest & newest records
        in the input `DataFrame`.

    """
    if df is None or df.empty:
        raise ValueError("Missing or empty DataFrame")
    if date_col is None:
        raise ValueError("Missing name of date column to sort by")

    try:
        min_date = df[date_col].min()
        oldest = df.loc[df[date_col] == min_date]

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting min date value from column [{date_col}]. Details: {exc}"
        )
        log.error(msg)

        raise exc

    try:
        max_date = df[date_col].max()
        newest = df.loc[df[date_col] == max_date]

    except Exception as exc:
        msg = Exception(
            f"Unhandled exception getting max date value from column [{date_col}]. Details: {exc}"
        )
        log.error(msg)

        raise exc

    if filter_cols is not None:
        try:
            oldest = oldest[filter_cols]
            newest = newest[filter_cols]
        except Exception as exc:
            msg = Exception(f"Unhandled exception filtering columns. Details: {exc}")
            log.error(msg)

            raise exc

    return oldest, newest


def convert_df_col_dtypes(df: pd.DataFrame, dtype_mapping: dict) -> pd.DataFrame:
    """Converts the specified columns in a DataFrame to the given data types.

    Params:
        df (pd.DataFrame): The input DataFrame.
        dtype_mapping (dict): A dictionary where keys are column names and values are the target data types.

    Returns:
        pd.DataFrame: The DataFrame with converted column types.

    """
    try:
        return df.astype(dtype_mapping)
    except KeyError as e:
        raise ValueError(f"Column not found: {e}")
    except ValueError as e:
        raise ValueError(f"Invalid data type conversion: {e}")
    

def convert_df_datetimes_to_timestamp(df: pd.DataFrame):
    """Convert all datetime columns in the DataFrame to Unix timestamps (integers).
    
    Params:
    - df (pandas.DataFrame): The DataFrame to be processed.
    
    Returns:
    - pandas.DataFrame: The DataFrame with all datetime columns converted to timestamps.

    """
    # Iterate over each column in the DataFrame
    for column in df.columns:
        # Check if the column contains datetime-like data
        if pd.api.types.is_datetime64_any_dtype(df[column]):
            # Convert datetime to Unix timestamp (number of seconds since epoch)
            df[column] = df[column].apply(lambda x: int(x.timestamp()) if pd.notnull(x) else None)
    
    return df