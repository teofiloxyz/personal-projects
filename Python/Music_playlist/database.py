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
