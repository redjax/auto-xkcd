from __future__ import annotations

from contextlib import AbstractContextManager
from pathlib import Path
import typing as t

import duckdb
import ibis
from ibis.expr.types.relations import Table
from loguru import logger as log
import pandas as pd

class IbisDuckDBController(AbstractContextManager):
    def __init__(
        self,
        interactive: bool = True,
        duckdb_path: str = "duckdb://",
        memory_limit: str = "1GB",
        threads: int = 4,
    ):
        if duckdb_path:
            if not f"{duckdb_path}".startswith("duckdb://"):
                duckdb_path = f"duckdb://{duckdb_path}"

        self.interactive = interactive
        self.duckdb_path = duckdb_path
        self.memory_limit = memory_limit
        self.threads = threads

        self.connection = None

    def __enter__(self) -> t.Self:
        self.set_interactive()

        conn: ibis.BaseBackend = ibis.connect(
            resource=self.duckdb_path,
            threads=self.threads,
            memory_limit=self.memory_limit,
        )

        self.connection: ibis.BaseBackend = conn

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def set_interactive(self):
        if self.interactive:
            log.info("Enabling interactive Ibis.")
            ibis.options.interactive = True

    def create_table(
        self, tbl_name: str = None, schema: list[tuple] = None, overwrite: bool = True
    ) -> Table:
        raise NotImplementedError("Creating a table is not yet implemented")
        try:
            tbl: Table = ibis.table([], name=tbl_name)

            return tbl
        except Exception as exc:
            msg = Exception(f"Unhandled exception creating ibis Table. Details: {exc}")
            log.error(msg)
            log.trace(exc)

            raise exc

    def save_to_db(
        self, db_tbl_name: str = None, ibis_tbl: Table = None, overwrite: bool = False
    ) -> Table:
        try:
            db_tbl: Table = self.connection.create_table(
                db_tbl_name, ibis_tbl, overwrite=True
            )

            log.success(f"Ibis Table saved to database table '{db_tbl_name}'.")

            return db_tbl
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception writing to table '{db_tbl_name}' in database. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            raise exc

    def read_pq(
        self,
        pq_file: t.Union[str, Path] = None,
        write_to_db: bool = True,
        db_tbl_name: str = None,
    ) -> Table:
        pq_file: Path = Path(f"{pq_file}")

        try:
            t: Table = self.connection.read_parquet(pq_file)
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception reading Parquet file '{pq_file}'. Details: {exc}"
            )
            log.error(msg)
            log.trace(exc)

            raise exc

        if write_to_db:
            if not db_tbl_name:
                raise ValueError("write_to_db is True, but missing a db_tbl_name.")

            try:
                self.save_to_db(db_tbl_name=db_tbl_name, ibis_tbl=t, overwrite=True)
            except Exception as exc:
                msg = Exception(
                    f"Unhandled exception saving ibis Table to database table '{db_tbl_name}'. Details: {exc}"
                )
                log.error(msg)

                log.warning(f"Table not saved, but exists in memory.")

        return t

    def add_row(
        self, new_row: t.Union[dict, pd.DataFrame] = None, existing_tbl: Table = None
    ):
        raise NotImplementedError("Adding rows is not yet implemented")


class DuckDBController(AbstractContextManager):
    def __init__(self, db_path=":memory:"):  # noqa: D107
        self.db_path = Path(db_path)
        self.connection = None

    def __enter__(self):  # noqa: D105
        self.connection = duckdb.connect(str(self.db_path))
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # noqa: D105
        if self.connection:
            self.connection.close()
        if exc_type is not None:
            return False

    def get_tables(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
            )
            return [row[0] for row in cursor.fetchall()]

    def create_table(self, table_name: str = None, schema: str = None):
        with self.connection.cursor() as cursor:
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})")

    def _multi_pq_load(self, scan_dir: t.Union[str, Path] = None):
        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM read_parquet('{scan_dir}/*.parquet')")

    def _pq_load(self, pq_file: t.Union[str, Path] = None):
        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM read_parquet('{pq_file}')")

    def load_pq(self, pq: t.Union[str, Path, list[str | Path]] = None):
        if isinstance(pq, str) or isinstance(pq, Path):
            pq: Path = Path(f"{pq}")

        if pq.is_file():
            log.debug("pq is a file")
            self._pq_load(pq_file=pq)
        elif pq.is_dir():
            log.debug("pq is a dir")
            self._multi_pq_load(scan_dir=pq)

        #     self._pq_load(pq_file=pq)
        # elif isinstance(pq, list):
        #     _lst = []

        #     for i in pq:
        #         _i = Path(f"{i}")
        #         _lst.append(_i)

        #     pq: list = _lst

        #     self._multi_pq_load()

    def drop_table(self, table_name: str = None):
        with self.connection.cursor() as cursor:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

    def drop_rows(self, table_name, condition):
        with self.connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM {table_name} WHERE {condition}")

    def delete_database_file(self):
        if self.db_path != ":memory:":
            if self.db_path.exists():
                self.db_path.unlink()
