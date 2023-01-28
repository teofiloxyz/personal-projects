import pandas as pd

import sqlite3


class Database:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def __enter__(self) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
        self.db_con = sqlite3.connect(self.db_path)
        self.cursor = self.db_con.cursor()
        return self.db_con, self.cursor

    def __exit__(self, *args) -> None:
        self.db_con.close()


class Query:
    def __init__(self, db_path: str) -> None:
        self.db = Database(db_path)

    def get_tabs(self) -> list[str]:
        with self.db as (_, db_cursor):
            db_cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        return db_cursor.fetchall()

    def create_df(self, db_table: str) -> pd.DataFrame:
        with self.db as (db_con, _):
            return pd.read_sql(f"SELECT * FROM {db_table}", db_con)

    def export_tab_to_csv(self, csv_output: str, db_table: str) -> None:
        with self.db as (db_con, _):
            df = pd.read_sql(f"SELECT * FROM {db_table}", db_con)
            df.to_csv(csv_output, encoding="utf-8", index=False)

    def get_tab_columns(self, db_table: str) -> list[str]:
        with self.db as (_, db_cursor):
            db_cursor.execute(f"pragma table_info({db_table})")
            return db_cursor.fetchall()


class Edit:
    def __init__(self, db_path: str) -> None:
        self.db = Database(db_path)

    def add_entry(self, table: str, entry: tuple) -> None:
        db_cmd = f"INSERT INTO {table} VALUES {entry}"
        self._execute(db_cmd)

    def remove_entry(self, table: str, rowid: str) -> None:
        db_cmd = f"DELETE FROM {table} WHERE rowid={rowid}"
        self._execute(db_cmd)

    def create_tab(self, table: str, columns: str) -> None:
        db_cmd = f"CREATE TABLE {table} ({columns})"
        self._execute(db_cmd)

    def remove_tab(self, table: str) -> None:
        db_cmd = f"DROP TABLE {table}"
        self._execute(db_cmd)

    def create_tab_from_csv(self, csv_input: str, tab_name: str) -> None:
        with self.db as (db_con, _):
            df = pd.read_csv(csv_input)
            df.to_sql(tab_name, db_con, index=False)

    def _execute(self, db_cmd: str) -> None:
        with self.db as (db_con, db_cursor):
            db_cursor.execute(db_cmd)
            db_con.commit()
