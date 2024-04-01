from __future__ import annotations

from pathlib import Path
import typing as t

from .constants import COMIC_NUMS_CSV

from loguru import logger as log
import pandas as pd


class ComicNumsController:
    def __init__(self, filename: t.Union[str, Path] | None = COMIC_NUMS_CSV):
        if filename is None:
            self.filename: Path = filename
        else:
            assert isinstance(filename, str) or isinstance(filename, Path), TypeError(
                f"{self.logstr}.filename must be a string or Path. Got type: ({type(filename)})"
            )
            if isinstance(filename, str):
                if "~" in filename:
                    filename: Path = Path(filename).expanduser()
                else:
                    filename: Path = Path(filename)

        self.filename = filename
        self.df = pd.DataFrame()

    @property
    def logstr(self) -> str:
        return "@ComicNumsController >"

    def __enter__(self):
        if self.filename.exists():
            try:
                self.df = pd.read_csv(self.filename, lineterminator="\n")
            except Exception as exc:
                msg = Exception(
                    f"{self.logstr} Unhandled exception loading CSV contents into DataFrame. Details: {exc}"
                )
                raise msg

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if isinstance(self.df, pd.DataFrame):
            if self.df.empty:
                log.warning(f"DataFrame is empty.")

                return

            try:
                self.df_drop_duplicates()
                ## Sort column after all other cleaning
                self.sort_by_comic_num()
            except Exception as exc:
                msg = Exception(
                    f"{self.logstr} Unhandled exception cleaning DataFrame. Details: {exc}"
                )
                log.error(msg)

            try:
                self.df["comic_num"] = self.df["comic_num"].astype(int)
            except Exception as exc:
                msg = Exception(
                    f"{self.logstr} Unhandled exception converting comic_num column to int. Details: {exc}"
                )
                log.error(msg)

                raise msg

            try:
                self.df.to_csv(self.filename, index=False, lineterminator=f"\n")
                # log.success(f"DataFrame saved to '{self.filename}'")
            except Exception as exc:
                msg = Exception(
                    f"{self.logstr} Unhandled exception saving DataFrame to file '{self.filename}'. Details: {exc}."
                )
                log.error(
                    f"{self.logstr} exception:\n\texc_type: {exc_type}\n\texc_value: {exc_value}\n\ttraceback: {traceback}"
                )

                raise msg

    def add_comic_num_data(self, data: dict = None):
        assert data, ValueError(f"{self.logstr} Missing comic num data dict.")
        assert isinstance(data, dict), TypeError(
            f"data must be a dict. Got type: ({type(data)})"
        )

        try:
            new_row = pd.DataFrame([data])
            log.debug(f"New comic_num row ({type(new_row)}):\n{new_row}")
        except Exception as exc:
            msg = Exception(
                f"{self.logstr} Unhandled exception creating DataFrame row from input data. Details: {exc}"
            )

            raise msg

        _num = data["comic_num"]

        assert isinstance(self.df, pd.DataFrame), TypeError(
            f"self.df should be type pd.DataFrame. Got type: ({type(self.df)})"
        )
        if self.df.empty:
            ## self.df is empty, concatenate with new row data
            try:
                self.df: pd.DataFrame = pd.concat([self.df, new_row], ignore_index=True)

            except Exception as exc:
                msg = Exception(
                    f"{self.logstr} Unhandled exception adding new data row to DataFrame. Details: {exc}"
                )

                raise msg
        else:
            ## DataFrame has contents, search & update row
            if _num in self.df["comic_num"].to_list():
                log.debug(
                    f"{self.logstr} Found comic #{_num} in CSV file. Updating value(s)"
                )

                try:
                    row: pd.DataFrame = self.df.loc[self.df["comic_num"] == _num]
                    log.debug(
                        f"{self.logstr} Comic #{_num} existing row ({type(row)}):\n{row}"
                    )
                except Exception as exc:
                    msg = Exception(
                        f"Unhandled exception extracting row matching comic_num: [{_num}]. Details: {exc}"
                    )
                    log.error(msg)

                    raise msg

                row = new_row
                log.debug(f"Updated row:\n{row}")
                try:
                    new_df = self.df.update(row, overwrite=True)
                    log.debug(f"New dataframe:\n{new_df}")
                    self.df = new_df
                    log.success(f"Updated comic #{_num} data.")
                except Exception as exc:
                    msg = Exception(f"Unhandled exception updating row. Details: {exc}")
                    log.error(msg)

                    raise msg
            else:
                # log.warning(f"Comic #{data['comic_num']} row not found. Adding row.")
                self.df = pd.concat([self.df, new_row])

        return self

    def highest(self) -> int | None:
        if self.df.empty:
            log.warning(f"No comic numbers have been recorded.")

            return

        return self.df["comic_num"].max()

    def df_drop_duplicates(self, subset: list[str] = ["comic_num"]):
        assert isinstance(self.df, pd.DataFrame), TypeError(
            f"self.df should be a DataFrame. Got type: ({type(self.df)})"
        )
        if self.df.empty:
            log.warning(f"DataFrame is empty, skipping duplicates drop.")
            return

        try:
            self.df = self.df.drop_duplicates(subset=subset)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception dropping duplicates from DataFrame. Details: {exc}"
            )

            raise msg

    def sort_by_comic_num(self, sort_col: str = "comic_num"):
        if self.df.empty:
            log.warning(f"DataFrame is empty, skipping sort.")
            return

        try:
            sorted: pd.DataFrame = self.df.sort_values(by=sort_col)
            self.df = sorted
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception sorting DataFrame by column '{sort_col}'. Details: {exc}"
            )
            log.error(msg)

            raise msg

    def as_list(self) -> list[int]:
        try:
            comic_nums: list[int] = self.df["comic_num"].to_list()

            return comic_nums
        except KeyError as key_err:
            msg = Exception(
                f"Could not load list of comic_nums from DataFrame. Is the DataFrame empty?"
            )
            log.error(msg)

            return []
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception creating list of comic nums. Details: {exc}"
            )
            log.error(msg)

            raise msg
