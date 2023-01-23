import pandas as pd

import os
import sqlite3


class Database:
    def __init__(self) -> None:
        self.db_path = "music_playlist.db"
        if not os.path.isfile(self.db_path):
            self._setup_database()

    def __enter__(self) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
        self.db_con = sqlite3.connect(self.db_path)
        self.cursor = self.db_con.cursor()
        return self.db_con, self.cursor

    def __exit__(self, *args) -> None:
        self.db_con.close()

    def _create_playlist_table(self, playlist: str) -> None:
        self.cursor.execute(
            f"CREATE TABLE {playlist}(music_id INTEGER PRIMARY KEY "
            "AUTOINCREMENT NOT NULL UNIQUE, date_added TEXT NOT NULL, "
            "title TEXT NOT NULL UNIQUE, ytb_code TEXT NOT NULL UNIQUE, "
            "genre TEXT NOT NULL)"
        )
        self.db_con.commit()

    def _create_genres_table(self) -> None:
        self.cursor.execute("CREATE TABLE genres(genre TEXT NOT NULL UNIQUE)")
        self.db_con.commit()

    def _setup_database(self) -> None:
        open(self.db_path, "x")
        with self as (self.db_con, self.cursor):
            self._create_playlist_table("playlist")
            self._create_playlist_table("archive")
            self._create_genres_table()


class Query:
    def __init__(self) -> None:
        self.db = Database()

    def get_all_music(self, playlist: str, selection: str) -> pd.DataFrame:
        query = f"SELECT {selection} FROM {playlist}"
        return self._create_df(query)

    def get_all_titles(self, playlist: str) -> list:
        query = f"SELECT title FROM {playlist}"
        return [title[0] for title in self._create_df(query).values]

    def get_all_genres(self) -> list:
        query = "SELECT genre FROM genres"
        return [genre[0] for genre in self._create_df(query).values]

    def get_title_with_search(
        self, playlist: str, column: str, search: str
    ) -> list:
        query = f'SELECT title FROM {playlist} WHERE {column} like "%{search}%"'
        return [title[0] for title in self._create_df(query).values]

    def get_title_with_id(self, playlist: str, music_id: int) -> str:
        query = f"SELECT title FROM {playlist} WHERE music_id={music_id}"
        return self._create_df(query).values[0]

    def get_selection_with_title(
        self, playlist: str, selection: str, title: str
    ) -> list:
        query = f'SELECT {selection} FROM {playlist} WHERE title="{title}"'
        return self._create_df(query).values[0]

    def check_if_link_exists(self, playlist: str, ytb_code: str) -> bool:
        query = f'SELECT * FROM {playlist} WHERE ytb_code="{ytb_code}"'
        result = self._create_df(query).values
        if not result:
            return False
        return True

    def export_transactions_to_csv(
        self, playlist: str, csv_output: str
    ) -> None:
        query = f"SELECT * FROM {playlist}"
        df = self._create_df(query)
        df.to_csv(csv_output, encoding="utf-8", index=False)

    def _create_df(self, db_query: str) -> pd.DataFrame:
        with self.db as (db_con, _):
            return pd.read_sql(db_query, db_con)


class Edit:
    def __init__(self) -> None:
        self.db = Database()

    def add_music(self, playlist: str, entry: tuple) -> None:
        db_cmd = (
            f"INSERT INTO {playlist} (date_added, title, "
            f"ytb_code, genre) VALUES {entry}"
        )
        self._execute(db_cmd)

    def add_genre(self, genre: str) -> None:
        db_cmd = f'INSERT INTO genres (genre) VALUES ("{genre}")'
        self._execute(db_cmd)

    def remove_music(self, playlist: str, title: str) -> None:
        db_cmd = f'DELETE FROM {playlist} WHERE title="{title}"'
        self._execute(db_cmd)

    def update_playlist(
        self, playlist: str, column: str, new_name: str, title: str
    ) -> None:
        db_cmd = (
            f'UPDATE {playlist} SET {column}="{new_name}" WHERE title="{title}"'
        )
        self._execute(db_cmd)

    def import_csv(self, playlist: str, csv_input: str) -> None:
        df = pd.read_csv(csv_input)
        with self.db as (db_con, _):
            df.to_sql(playlist, db_con, if_exists="replace")

    def _execute(self, db_cmd: str) -> None:
        with self.db as (db_con, cursor):
            cursor.execute(db_cmd)
            db_con.commit()
