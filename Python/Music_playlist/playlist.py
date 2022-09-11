from configparser import ConfigParser

from database import Database


class Playlist:
    def __init__(self, playlist: str) -> None:
        self.config = ConfigParser()
        self.config.read("config.ini")
        self.music_path = self.config["GENERAL"]["music_path"]
        self.playlist = playlist

    def show(self, mode: str) -> None:
        selection = "*" if mode == "all" else "music_id, title"
        df = Database().Query().create_df(self.playlist, selection)
        if len(df) == 0:
            print(f"{self.playlist.capitalize()} is empty...")
            return
        print(df.to_string(index=False))
