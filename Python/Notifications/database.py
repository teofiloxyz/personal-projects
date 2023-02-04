import os
import sqlite3

from notifs import Notif, Urgency


class Database:
    def __init__(self) -> None:
        self.db_path = "notifications.db"
        if not os.path.isfile(self.db_path):
            self._setup_database()

    def __enter__(self) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
        self.db_con = sqlite3.connect(self.db_path)
        self.cursor = self.db_con.cursor()
        return self.db_con, self.cursor

    def __exit__(self, *args) -> None:
        self.db_con.close()

    def _create_table(self, title: str) -> None:
        self.cursor.execute(
            f"CREATE TABLE {title}(notif_id INTEGER PRIMARY KEY "
            "AUTOINCREMENT NOT NULL UNIQUE, date TEXT NOT NULL, "
            "hour TEXT NOT NULL, title TEXT NOT NULL, "
            "message TEXT, urgency TEXT NOT NULL, "
            "category TEXT, uid TEXT)"
        )
        self.db_con.commit()

    def _setup_database(self) -> None:
        open(self.db_path, "x")
        with self as (self.db_con, self.cursor):
            self._create_table("history")
            self._create_table("unseen")
            self._create_table("scheduled")


class Query:
    def __init__(self) -> None:
        self.db = Database()

    def get_history(self, days_delta: int = 15) -> list[Notif]:
        query = (
            "SELECT * FROM history "
            f"WHERE date >= datetime('now', '-{days_delta} days')"
        )
        results = self._fetch_results(query)
        return [self._get_notif_with_results(notif) for notif in results]

    def get_all_unseen(self) -> list[Notif]:
        query = f"SELECT * FROM unseen"
        results = self._fetch_results(query)
        return [self._get_notif_with_results(notif) for notif in results]

    def get_scheduled(self, days_delta: int = 15) -> list[Notif]:
        query = (
            "SELECT * FROM scheduled "
            f"WHERE date <= datetime('now', '+{days_delta} days')"
        )
        results = self._fetch_results(query)
        return [self._get_notif_with_results(notif) for notif in results]

    def _fetch_results(self, query: str) -> list:
        with self.db as (_, db_cursor):
            db_cursor.execute(query)
            return db_cursor.fetchall()

    def _get_notif_with_results(self, notif_db_entry: tuple) -> Notif:
        """notif_id isn't used on Notif object; also need to correct urg"""

        notif = Notif(*notif_db_entry[1:])
        notif.urgency = Urgency(notif.urgency)
        return notif


class Edit:
    def __init__(self) -> None:
        self.db = Database()

    def add_to_history(self, notif: Notif) -> None:
        self._add_to_table("history", notif)

    def add_to_unseen(self, notif: Notif) -> None:
        self._add_to_table("unseen", notif)

    def add_to_scheduled(self, notif: Notif) -> None:
        self._add_to_table("scheduled", notif)

    def _add_to_table(self, table: str, notif: Notif) -> None:
        db_cmd = (
            f"INSERT INTO {table} "
            "(date, hour, title, message, urgency, category, uid)"
            f'VALUES("{notif.date}", "{notif.hour}", "{notif.title}", '
            f'"{notif.message}", "{notif.urgency.value}", '
            f'"{notif.category}", "{notif.uid}")'
        )
        self._execute(db_cmd)

    def remove_all_from_unseen(self) -> None:
        db_cmd = "DELETE FROM unseen"
        self._execute(db_cmd)

    def remove_from_scheduled(self, notif: Notif) -> None:
        db_cmd = (
            f'DELETE FROM scheduled WHERE date="{notif.date}" '
            f'AND hour="{notif.hour}" '
            f'AND title="{notif.title}" AND message="{notif.message}"'
        )
        self._execute(db_cmd)

    def update_on_scheduled(self, notif: Notif, new_notif: Notif) -> None:
        db_cmd = (
            f'UPDATE scheduled SET date="{new_notif.date}", '
            f'hour="{new_notif.hour}", message="{new_notif.message}" '
            f'WHERE date="{notif.date}" AND hour="{notif.hour}" '
            f'AND title="{notif.title}" AND message="{notif.message}"'
        )
        self._execute(db_cmd)

    def _execute(self, db_cmd: str) -> None:
        with self.db as (db_con, cursor):
            cursor.execute(db_cmd)
            db_con.commit()
