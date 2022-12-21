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
        Faço assim pela experiência de usar foreign key"""
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

        def get_transaction_from_id(self, tid: int) -> tuple:
            self.cursor.execute(
                f"SELECT * FROM transactions WHERE transaction_id = {tid}"
            )
            transaction = self.cursor.fetchone()
            self.db.disconnect()
            return transaction

        def get_last_transaction(self) -> tuple:
            self.cursor.execute(
                "SELECT * FROM transactions ORDER BY "
                "transaction_id DESC LIMIT 1"
            )
            transaction = self.cursor.fetchone()
            self.db.disconnect()
            return transaction

        def create_df_with_transactions(
            self,
            selection: str = "*",
        ) -> pd.DataFrame:
            db_query = (
                f"SELECT {selection} FROM transactions LEFT JOIN expenses "
                "USING(transaction_id)"
            )
            return self.create_df(db_query)

        def create_df_with_revenue(
            self,
            selection: str = "*",
        ) -> pd.DataFrame:
            db_query = (
                f"SELECT {selection} FROM transactions "
                'WHERE trn_type = "Revenue"'
            )
            return self.create_df(db_query)

        def create_df_with_expenses(
            self,
            selection: str = "*",
        ) -> pd.DataFrame:
            db_query = (
                f"SELECT {selection} FROM transactions LEFT JOIN expenses "
                'USING(transaction_id) WHERE trn_type = "Expense"'
            )
            return self.create_df(db_query)

        def create_df(self, db_query: str) -> pd.DataFrame:
            df = pd.read_sql(db_query, self.db_con)
            self.db.disconnect()
            return df

    class Edit:
        def __init__(self) -> None:
            self.db = Database()
            self.db_con, self.cursor = self.db.connect()

        def add_transaction(self, entry: tuple) -> None:
            db_cmd = (
                "INSERT INTO transactions (time, "
                f"trn_type, amount, note) VALUES {entry}"
            )
            self.execute(db_cmd)

        def remove_transaction(
            self, trn_id: int, is_expense: bool = False
        ) -> None:
            """Infelizmente DELETE ON CASCADE ñ está a resultar; improve"""

            if is_expense:
                db_cmd = f"DELETE FROM expenses WHERE transaction_id = {trn_id}"
                self.cursor.execute(db_cmd)
                self.db_con.commit()

            db_cmd = f"DELETE FROM transactions WHERE transaction_id = {trn_id}"
            self.execute(db_cmd)

        def add_expense(self, category: str, trn_id: str) -> None:
            db_cmd = (
                "INSERT INTO expenses (transaction_id, "
                f"category) VALUES {trn_id, category}"
            )
            self.execute(db_cmd)

        def execute(self, db_cmd: str) -> None:
            self.cursor.execute(db_cmd)
            self.db_con.commit()
            self.db.disconnect()
