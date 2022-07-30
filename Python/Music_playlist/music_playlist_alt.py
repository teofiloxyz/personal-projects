#!/usr/bin/python3
# MusicPlaylist menu com diversas funções, versão alternativa

import sqlite3
from Tfuncs import gmenu


class MusicPlaylist:
    def __init__(self):
        pass

    def setup_database(self):
        pass

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
