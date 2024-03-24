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
                f"filename must be a string or Path. Got type: ({type(filename)})"
            )
            if isinstance(filename, str):
                if "~" in filename:
                    filename: Path = Path(filename).expanduser()
                else:
                    filename: Path = Path(filename)

        self.filename = filename
        self.df = pd.DataFrame()

    def __enter__(self):
        if self.filename.exists():
            try:
                self.df = pd.read_csv(self.filename)
            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception loading CSV contents into DataFrame. Details: {exc}"
                )
                raise msg

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.df_drop_duplicates()
        self.sort_by_comic_num()

        try:
            self.df.to_csv(self.filename, index=False)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception saving DataFrame to file '{self.filename}'. Details: {exc}."
            )
            print(
                f"@ComicNumsController exception:\n\texc_type: {exc_type}\n\texc_value: {exc_value}\n\ttraceback: {traceback}"
            )

            raise msg

    def add_comic_num_data(self, data: dict = None):
        assert data, ValueError("Missing comic num data dict.")
        assert isinstance(data, dict), TypeError(
            f"data must be a dict. Got type: ({type(data)})"
        )

        try:
            new_row = pd.DataFrame([data])
            log.debug(f"New comic_num row ({type(new_row)}):\n{new_row}")
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception creating DataFrame row from input data. Details: {exc}"
            )

            raise msg

        _num = data["comic_num"]

        if not self.df.empty:

            if _num in self.df["comic_num"].to_list():
                log.debug(f"Found comic #{_num} in CSV file. Updating value(s)")

                row = self.df[self.df["comic_num"] == _num]
                img_saved = row["img_saved"].iloc[0]

                if not img_saved == data["img_saved"]:
                    log.warning(
                        f"Comic num {_num} already exists in DataFrame. Updating data."
                    )
                    self.df[self.df["comic_num"] == _num] = new_row

                return
            else:
                log.debug(f"Saving comic #{_num} to CSV file")

                try:
                    self.df = pd.concat([self.df, new_row], ignore_index=True)
                except Exception as exc:
                    msg = Exception(
                        f"Unhandled exception adding new data row to DataFrame. Details: {exc}"
                    )

                    raise msg

        else:

            try:
                self.df = pd.concat([self.df, new_row], ignore_index=True)
            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception adding new data row to DataFrame. Details: {exc}"
                )

                raise msg

    def highest(self) -> int | None:
        if self.df.empty:
            log.warning(f"No comic numbers have been recorded.")

            return

        return self.df["comic_num"].max()

    def df_drop_duplicates(self, subset: list[str] = ["comic_num"]):
        if self.df.empty:
            log.warning(f"DataFrame is empty, skipping duplicates drop.")
            return

        try:
            self.df = self.df.drop_duplicates(subset=["comic_num"])
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
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception creating list of comic nums. Details: {exc}"
            )
            log.error(msg)

            raise msg
