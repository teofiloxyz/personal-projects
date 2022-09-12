import pandas as pd

import os
import subprocess
import sqlite3
from configparser import ConfigParser


class Database:
    def __init__(self) -> None:
        self.config = ConfigParser()
        self.config.read("config.ini")
        self.db_path = self.config["GENERAL"]["db_path"]
        if not os.path.isfile(self.db_path):
            self.setup_database()

    def connect(self) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
        self.db_con = sqlite3.connect(self.db_path)
        self.cursor = self.db_con.cursor()
        return self.db_con, self.cursor

    def disconnect(self) -> None:
        self.db_con.close()

    def create_table(self, playlist: str) -> None:
        self.cursor.execute(
            f"CREATE TABLE {playlist}(music_id "
            "INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL "
            "UNIQUE, date_added TEXT NOT NULL, title TEXT "
            "NOT NULL UNIQUE, ytb_code TEXT NOT NULL UNIQUE, "
            "genre TEXT NOT NULL)"
        )
        self.db_con.commit()

    def reset_table(self, playlist: str) -> None:
        self.connect()
        self.cursor.execute(f"DROP TABLE {playlist}")
        self.db_con.commit()
        self.create_table(playlist)
        self.disconnect()

    def setup_database(self) -> None:
        subprocess.run(["touch", self.db_path])
        self.connect()
        self.create_table("playlist")
        self.create_table("archive")
        self.cursor.execute("CREATE TABLE genres(genre TEXT NOT NULL UNIQUE)")
        self.db_con.commit()
        self.disconnect()

    class Query:
        def __init__(self) -> None:
            self.db = Database()
            self.db_con, self.cursor = self.db.connect()

        def create_df(self, playlist: str, selection: str) -> pd.DataFrame:
            df = pd.read_sql(
                f"SELECT {selection} FROM {playlist} ORDER BY music_id",
                self.db_con,
            )
            self.db.disconnect()
            return df

        def get_title_with_search(
            self, playlist: str, column: str, search: str
        ) -> tuple:
            self.cursor.execute(
                f'SELECT title FROM {playlist} WHERE {column} like "%{search}%"'
            )
            result = tuple([title[0] for title in self.cursor.fetchall()])
            self.db.disconnect()
            return result

        def get_selection_with_title(
            self, playlist: str, selection: str, title: str
        ) -> tuple:
            self.cursor.execute(
                f'SELECT {selection} FROM {playlist} WHERE title="{title}"'
            )
            result = self.cursor.fetchone()
            self.db.disconnect()
            return result

        def get_all_titles(self, playlist: str) -> tuple:
            self.cursor.execute(f"SELECT title FROM {playlist}")
            result = tuple([title[0] for title in self.cursor.fetchall()])
            self.db.disconnect()
            return result

        def get_all_genres(self) -> tuple:
            self.cursor.execute("SELECT genre FROM genres")
            genres = tuple([genre[0] for genre in self.cursor.fetchall()])
            self.db.disconnect()
            return genres

        def get_title_with_id(self, playlist: str, music_id: int) -> str:
            self.cursor.execute(
                f"SELECT title FROM {playlist} WHERE music_id={music_id}"
            )
            result = self.cursor.fetchone()
            self.db.disconnect()
            return result

        def check_if_link_exists(self, playlist: str, ytb_code: str) -> bool:
            self.cursor.execute(
                f'SELECT * FROM {playlist} WHERE ytb_code="{ytb_code}"'
            )
            result = self.cursor.fetchone()
            self.db.disconnect()
            if result is None:
                return False
            print(f"Already have that youtube code on the {playlist}")
            return True

    class Edit:
        def __init__(self) -> None:
            self.db = Database()
            self.db_con, self.cursor = self.db.connect()

        def add(self, playlist: str, entry: tuple, title: str) -> None:
            self.cursor.execute(
                f"INSERT INTO {playlist} (date_added, title, "
                f"ytb_code, genre) VALUES {entry}"
            )
            self.db_con.commit()
            print(f'"{title}" added to the {playlist}!')
            self.db.disconnect()

        def add_genre(self, genre: str) -> None:
            self.cursor.execute(
                f'INSERT INTO genres (genre) VALUES ("{genre}")'
            )
            self.db_con.commit()
            print(f'"{genre}" saved to genres!')
            self.db.disconnect()

        def remove(self, playlist: str, title: str) -> None:
            self.cursor.execute(f'DELETE FROM {playlist} WHERE title="{title}"')
            self.db_con.commit()
            print(f'"{title}" removed from the {playlist}!')
            self.db.disconnect()

        def update(
            self, playlist: str, column: str, new_name: str, title: str
        ) -> None:
            self.cursor.execute(
                f'UPDATE {playlist} SET {column}="{new_name}"'
                f'WHERE title="{title}"'
            )
            self.db_con.commit()
            self.db.disconnect()
