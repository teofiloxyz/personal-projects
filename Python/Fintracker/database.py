#!/usr/bin/python3

import pandas as pd

import subprocess
import sqlite3


class Database:
    def __init__(self) -> None:
        self.db_path = self.json_info["db_path"]
        if not os.path.isfile(self.db_path):
            self.setup_database()

    def connect(self) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
        self.db_con = sqlite3.connect(self.db_path)
        self.cursor = self.db_con.cursor()
        return self.db_con, self.cursor

    def disconnect(self) -> None:
        self.db_con.close()

    def setup_database(self) -> None:
        subprocess.run(["touch", self.db_path])
        self.connect()
        self.cursor.execute(
            "CREATE TABLE transactions(transaction_id "
            "INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL "
            "UNIQUE, time TEXT NOT NULL, trn_type TEXT "
            "NOT NULL, amount REAL NOT NULL, note TEXT)"
        )
        """Eu sei que podia ficar tudo numa tabela com category NULL
        Faço assim para usar foreign key"""
        self.cursor.execute(
            "CREATE TABLE expenses(transaction_id "
            "INTEGER, category TEXT NOT NULL, "
            "FOREIGN KEY(transaction_id) "
            "REFERENCES transactions(transaction_id))"
        )
        self.db_con.commit()
        self.disconnect()

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
