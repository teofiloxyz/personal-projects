#!/usr/bin/python3
# MusicPlaylist menu com diversas funções, versão alternativa

import os
import subprocess
import sqlite3
from Tfuncs import gmenu
from configparser import ConfigParser


class MusicPlaylist:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read('config.ini')
        self.db_path = self.config['GENERAL']['db_path']
        self.music_path = self.config['GENERAL']['music_path']
        self.playlist_txt_path = self.config['GENERAL']['playlist_txt_path']
        self.search_utils_path = self.config['GENERAL']['search_utils_path']
        self.downloads_path = self.config['GENERAL']['downloads_path']

        if not os.path.isfile(self.db_path):
            self.setup_database()

    def setup_database(self):
        subprocess.run(['touch', self.db_path])

        self.db_con = sqlite3.connect(self.db_path)
        self.cursor = self.db_con.cursor()

        self.cursor.execute('CREATE TABLE active(music_id '
                            'INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL '
                            'UNIQUE, date_added TEXT NOT NULL, title TEXT '
                            'NOT NULL UNIQUE, ytb_code TEXT NOT NULL UNIQUE, '
                            'genre TEXT NOT NULL)')
        self.cursor.execute('CREATE TABLE archive(music_id '
                            'INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL '
                            'UNIQUE, date_added TEXT NOT NULL, title TEXT '
                            'NOT NULL UNIQUE, ytb_code TEXT NOT NULL UNIQUE, '
                            'genre TEXT NOT NULL)')
        self.cursor.execute('CREATE TABLE genres(genre TEXT NOT NULL UNIQUE)')
        self.db_con.commit()

        self.db_con.close()

    @staticmethod
    def generic_connection(func):
        def process(self, *args, **kwargs):
            self.db_con = sqlite3.connect(self.db_path)
            self.cursor = self.db_con.cursor()
            func(self, *args, **kwargs)
            self.db_con.close()
        return process

    def search(self):
        pass

    def play(self):
        pass

    def add(self):
        pass

    def remove(self):
        pass

    def recover_arc(self):
        pass

    def edit(self):
        pass

    def show(self):
        pass

    def youtube_search(self):
        pass

    def download(self):
        pass

    def export_csv(self):
        pass

    def import_csv(self):
        pass


if __name__ == "__main__":
    pl = MusicPlaylist()
    title = 'Music-Playlist-Menu'
    keys = {'p': (lambda: pl.play('playlist'),
                  "Play music from playlist"),
            'pa': (lambda: pl.play('archive'),
                   "Play music from archive"),
            'ad': (lambda: pl.add('playlist'),
                   "Add music to playlist"),
            'rm': (lambda: pl.remove('playlist'),
                   "Remove music from playlist that goes to archive"),
            'ada': (lambda: pl.add('archive'),
                    "Add music to archive"),
            'rma': (lambda: pl.remove('archive'),
                    "Remove music from archive"),
            'rc': (pl.recover_arc,
                   "Recover music from archive"),
            'ed': (lambda: pl.edit('playlist'),
                   "Edit title or genre of a music from playlist"),
            'eda': (lambda: pl.edit('archive'),
                    "Edit title or genre of a music from archive"),
            'ls': (lambda: pl.show('playlist', 'titles'),
                   "Show playlist titles"),
            'la': (lambda: pl.show('playlist', 'all'),
                   "Show all columns from playlist"),
            'lsa': (lambda: pl.show('archive', 'titles'),
                    "Show archive titles"),
            'laa': (lambda: pl.show('archive', 'all'),
                    "Show all columns from archive"),
            'y': (pl.youtube_search,
                  "Search music from youtube"),
            'd': (pl.download,
                  "Download from txt file with titles and/or links"),
            'xc': (pl.export_csv,
                   "Export playlist (or archive) to CSV"),
            'ic': (pl.import_csv,
                   "Import playlist (or archive) from CSV")}
    gmenu(title, keys)
