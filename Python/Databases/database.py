#!/usr/bin/python3

import pandas as pd

import sqlite3


class Database:
    def connect(
        self, db_path: str
    ) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
        self.db_con = sqlite3.connect(db_path)
        self.cursor = self.db_con.cursor()
        return self.db_con, self.cursor

    def disconnect(self) -> None:
        self.db_con.close()

    class Query:
        def __init__(self, db_path: str) -> None:
            self.db = Database()
            self.db_con, self.cursor = self.db.connect(db_path)

        def get_tabs(self) -> list[str]:
            self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tabs = self.cursor.fetchall()
            self.db.disconnect()
            return tabs

        def create_df(self, db_table: str) -> pd.DataFrame:
            df = pd.read_sql(f"SELECT * FROM {db_table}", self.db_con)
            self.db.disconnect()
            return df

        def get_tab_columns(self, db_table: str) -> list[str]:
            self.cursor.execute(f"pragma table_info({db_table})")
            columns = self.cursor.fetchall()
            self.db.disconnect()
            return columns

    class Edit:
        def __init__(self, db_path: str) -> None:
            self.db = Database()
            self.db_con, self.cursor = self.db.connect(db_path)

        def add_entry(self, table: str, entry: tuple) -> None:
            self.cursor.execute(f"INSERT INTO {table} VALUES {entry}")
            self.db_con.commit()
            self.db.disconnect()

        def remove_entry(self, table: str, rowid: str) -> None:
            self.cursor.execute(f"DELETE FROM {table} WHERE rowid={rowid}")
            self.db_con.commit()
            self.db.disconnect()

        def create_tab(self, table: str, columns: str) -> None:
            self.cursor.execute(f"CREATE TABLE {table} ({columns})")
            self.db_con.commit()
            self.db.disconnect()

        def remove_tab(self, table: str) -> None:
            self.cursor.execute(f"DROP TABLE {table}")
            self.db_con.commit()
            self.db.disconnect()

        def create_tab_from_csv(self, csv_input: str, tab_name: str) -> None:
            df = pd.read_csv(csv_input)
            df.to_sql(tab_name, self.db_con, index=False)
