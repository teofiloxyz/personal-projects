import pandas as pd

import os
import sqlite3


class Database:
    def __init__(self) -> None:
        self.db_path = "fintracker.db"
        if not os.path.isfile(self.db_path):
            self._setup_database()

    def __enter__(self) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
        self.db_con = sqlite3.connect(self.db_path)
        self.cursor = self.db_con.cursor()
        return self.db_con, self.cursor

    def __exit__(self, *args) -> None:
        self.db_con.close()

    def _setup_database(self) -> None:
        open(self.db_path, "x")
        with self as (db_con, cursor):
            cursor.execute(
                "CREATE TABLE transactions(transaction_id "
                "INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL "
                "UNIQUE, time TEXT NOT NULL, trn_type TEXT "
                "NOT NULL, amount REAL NOT NULL, note TEXT)"
            )
            """Eu sei que podia ficar tudo numa tabela com category NULL
            Faço assim somente pela experiência de usar foreign key"""
            cursor.execute(
                "CREATE TABLE expenses(transaction_id "
                "INTEGER, category TEXT NOT NULL, "
                "FOREIGN KEY(transaction_id) "
                "REFERENCES transactions(transaction_id))"
            )
            db_con.commit()


class Query:
    def __init__(self) -> None:
        self.db = Database()

    def get_categories(self) -> list:
        query = "SELECT DISTINCT category FROM expenses"
        return [category[0] for category in self._create_df(query).values]

    def get_transaction_from_id(self, tid: int) -> tuple:
        query = f"SELECT * FROM transactions WHERE transaction_id = {tid}"
        return self._create_df(query).values[0]

    def get_last_transaction(self) -> tuple:
        query = (
            "SELECT * FROM transactions ORDER BY transaction_id DESC LIMIT 1"
        )
        return self._create_df(query).values[0]

    def create_df_with_transactions(
        self,
        selection: str = "*",
    ) -> pd.DataFrame:
        query = (
            f"SELECT {selection} FROM transactions LEFT JOIN expenses "
            "USING(transaction_id)"
        )
        return self._create_df(query)

    def create_df_with_revenue(
        self,
        selection: str = "*",
    ) -> pd.DataFrame:
        query = (
            f"SELECT {selection} FROM transactions "
            'WHERE trn_type = "Revenue"'
        )
        return self._create_df(query)

    def create_df_with_expenses(
        self,
        selection: str = "*",
    ) -> pd.DataFrame:
        query = (
            f"SELECT {selection} FROM transactions LEFT JOIN expenses "
            'USING(transaction_id) WHERE trn_type = "Expense"'
        )
        return self._create_df(query)

    def export_transactions_to_csv(self, csv_output: str) -> None:
        df = self.create_df_with_transactions()
        df.to_csv(csv_output, encoding="utf-8", index=False)
        print(f"Export done")

    def _create_df(self, db_query: str) -> pd.DataFrame:
        with self.db as (db_con, _):
            return pd.read_sql(db_query, db_con)


class Edit:
    def __init__(self) -> None:
        self.db = Database()

    def add_transaction(self, entry: tuple) -> None:
        db_cmd = (
            "INSERT INTO transactions (time, "
            f"trn_type, amount, note) VALUES {entry}"
        )
        self._execute(db_cmd)

    def remove_transaction(self, trn_id: int, is_expense: bool = False) -> None:
        """Infelizmente DELETE ON CASCADE ñ está a resultar"""

        if is_expense:
            self.remove_expense(trn_id)
        db_cmd = f"DELETE FROM transactions WHERE transaction_id = {trn_id}"
        self._execute(db_cmd)

    def add_expense(self, category: str, trn_id: str) -> None:
        db_cmd = (
            "INSERT INTO expenses (transaction_id, "
            f"category) VALUES {trn_id, category}"
        )
        self._execute(db_cmd)

    def remove_expense(self, trn_id: int) -> None:
        db_cmd = f"DELETE FROM expenses WHERE transaction_id = {trn_id}"
        self._execute(db_cmd)

    def _execute(self, db_cmd: str) -> None:
        with self.db as (db_con, cursor):
            cursor.execute(db_cmd)
            db_con.commit()
