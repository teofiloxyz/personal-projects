#!/usr/bin/python3

import pandas as pd

import os
import subprocess
import sqlite3

from utils import Utils


class Database:
    def __init__(self) -> None:
        utils = Utils()
        json_info = utils.load_json()
        self.db_path = json_info["db_path"]
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
        Faço assim pela graça de usar foreign key"""
        self.cursor.execute(
            "CREATE TABLE expenses(transaction_id "
            "INTEGER, category TEXT NOT NULL, "
            "FOREIGN KEY(transaction_id) "
            "REFERENCES transactions(transaction_id))"
        )
        self.db_con.commit()
        self.disconnect()

    class Query:
        def __init__(self) -> None:
            self.db = Database()
            self.db_con, self.cursor = self.db.connect()

        def get_tabs(self) -> list[str]:
            self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tabs = self.cursor.fetchall()
            self.db.disconnect()
            return tabs

        def get_transactions_by_id(self, trn_id: int) -> tuple:
            self.cursor.execute(
                f"SELECT * FROM transactions WHERE transaction_id = {trn_id}"
            )
            trn_id_fetch = self.cursor.fetchone()
            self.db.disconnect()
            return trn_id_fetch

        def get_last_transaction(self) -> tuple:
            self.cursor.execute(
                "SELECT * FROM transactions ORDER BY "
                "transaction_id DESC LIMIT 1"
            )
            trn_id_fetch = self.cursor.fetchone()
            self.db.disconnect()
            return trn_id_fetch

        def create_df_of_expenses(self) -> pd.DataFrame:
            df = pd.read_sql(
                "SELECT SUBSTR(time, 1, 10) as date, amount, "
                "category FROM transactions LEFT JOIN expenses "
                "USING(transaction_id) WHERE "
                'trn_type = "Expense"',
                self.db_con,
            )
            self.db.disconnect()
            return df

        def create_df_trn_type(self, trn_type: str) -> pd.DataFrame:
            df = pd.read_sql(
                "SELECT SUBSTR(time, 1, 10) as date, amount FROM "
                f'transactions WHERE trn_type = "{trn_type}"',
                self.db_con,
            )
            self.db.disconnect()
            return df

        def create_df_transactions(self) -> pd.DataFrame:
            df = pd.read_sql("SELECT * FROM transactions", self.db_con)
            self.db.disconnect()
            return df

        def create_df_transactions_all(self) -> pd.DataFrame:
            df = pd.read_sql(
                "SELECT * FROM transactions LEFT JOIN expenses USING(transaction_id)",
                self.db_con,
            )
            self.db.disconnect()
            return df

        def create_df_transactions_expenses(self) -> pd.DataFrame:
            df = pd.read_sql(
                "SELECT * FROM transactions LEFT JOIN "
                "expenses USING(transaction_id) WHERE "
                'trn_type = "Expense"',
                self.db_con,
            )
            self.db.disconnect()
            return df

        def create_df_transactions_revenue(self) -> pd.DataFrame:
            df = pd.read_sql(
                "SELECT * FROM transactions WHERE " 'trn_type = "Revenue"',
                self.db_con,
            )
            self.db.disconnect()
            return df

        def get_tab_columns(self, db_table: str) -> list[str]:
            self.cursor.execute(f"pragma table_info({db_table})")
            columns = self.cursor.fetchall()
            self.db.disconnect()
            return columns

    class Edit:
        def __init__(self) -> None:
            self.db = Database()
            self.db_con, self.cursor = self.db.connect()

        def add_entry(self, table: str, entry: tuple) -> None:
            self.cursor.execute(f"INSERT INTO {table} VALUES {entry}")
            self.db_con.commit()
            self.db.disconnect()

        def add_transaction(self, entry: tuple) -> None:
            self.cursor.execute(
                "INSERT INTO transactions (time, "
                f"trn_type, amount, note) VALUES {entry}"
            )
            self.db_con.commit()
            self.db.disconnect()

        def add_expense(self, category: str, trn_id: str) -> None:
            self.cursor.execute(
                "INSERT INTO expenses (transaction_id, "
                f"category) VALUES {trn_id, category}"
            )
            self.db_con.commit()
            self.db.disconnect()

        def remove_transaction(self, trn_id: int) -> None:
            self.cursor.execute(
                f"DELETE FROM transactions WHERE transaction_id = {trn_id}"
            )
            self.db_con.commit()
            self.db.disconnect()

        def remove_expense(self, trn_id: int) -> None:
            self.cursor.execute(
                f"DELETE FROM expenses WHERE transaction_id = {trn_id}"
            )
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
