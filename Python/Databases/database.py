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

        def create_df(self, db_table: str) -> pd.DataFrame:
            df = pd.read_sql(f"SELECT * FROM {db_table}", self.db_con)
            self.db.disconnect()
            return df

    class Edit:
        def __init__(self, db_path: str) -> None:
            self.db = Database()
            self.db_con, self.cursor = self.db.connect(db_path)
