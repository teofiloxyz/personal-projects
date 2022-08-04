#!/usr/bin/python3
# MusicPlaylist menu com diversas funções, versão alternativa

import os
import subprocess
import sqlite3
import pandas as pd
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

    def search(self, table):
        while True:
            query = input('Enter music title to search: ')
            if query == 'q':
                print('Aborted...')
                return 'q'

            self.cursor.execute(f'SELECT title FROM {table} '
                                f'WHERE title like "%{query}%"')
            result = tuple([title[0] for title in self.cursor.fetchall()])

            if len(result) == 0:
                print(f"Nothing was found with '{query}' "
                      "on the title")
                continue
            else:
                return result

    @generic_connection
    def play(self, playlist):
        while True:
            print(f'\nls: Show {playlist} titles\ng: Search by genre\n'
                  's: Search by title\n#: Play music with # ID')
            option = input('Pick one of the options above '
                           f'or leave empty to play the whole {playlist}: ')

            if option == 'q':
                print('Aborted...')
                return

            elif option == 'ls':
                self.show(playlist, 'titles')
                # need to connect db again, bc show func closes database
                self.db_con = sqlite3.connect(self.db_path)
                self.cursor = self.db_con.cursor()

            elif option == 'g':
                while True:
                    self.cursor.execute('SELECT genre FROM genres')
                    genres = tuple([genre[0]
                                    for genre in self.cursor.fetchall()])
                    [print(f'[{n}] {genre}')
                     for n, genre in enumerate(genres, 1)]
                    selected_genres = input('Enter the genre number or combo '
                                            '(e.g: 2; 4+2+3): ')
                    selected_genres_list = []
                    for genre in selected_genres.split('+'):
                        try:
                            selected_genres_list.append(genres[int(genre) - 1])
                        except (ValueError, IndexError):
                            print('Aborted...')
                            return

                    selection = \
                        'title' if playlist == 'playlist' else 'ytb_code'
                    table = 'active' if playlist == 'playlist' else 'archive'
                    condition = \
                        '%" or genre like "%'.join(selected_genres_list)

                    self.cursor.execute(f'SELECT {selection} FROM {table} '
                                        f'WHERE genre like "%{condition}%"')

                    if playlist == 'playlist':
                        custom_list = tuple([f'"{title[0]}"*' for title
                                             in self.cursor.fetchall()])
                    else:
                        custom_list = tuple([f'https://youtu.be/{code[0]}' for
                                            code in self.cursor.fetchall()])

                    if len(custom_list) == 0:
                        selected_genres = ' or '.join(selected_genres_list)
                        print(f'Found none with genre: {selected_genres}\n')
                        continue
                    break
                break

            elif option == 's':
                table = 'active' if playlist == 'playlist' else 'archive'
                custom_list = self.search(table)
                if custom_list == 'q':
                    return
                elif len(custom_list) != 1:
                    [print(f'[{n}] {title}')
                     for n, title in enumerate(custom_list, 1)]
                    selected_titles = input('Enter the title number or combo '
                                            '(e.g: 2; 4+2+3) or leave empty '
                                            'for all: ')
                    if selected_titles != '':
                        selected_titles_list = []
                        for title in selected_titles.split('+'):
                            try:
                                selected_titles_list.append(custom_list
                                                            [int(title) - 1])
                            except (ValueError, IndexError):
                                print('Aborted...')
                                return
                        custom_list = tuple(selected_titles_list)

                if playlist == 'playlist':
                    custom_list = tuple([f'"{title}"*' for title
                                         in custom_list])
                else:
                    code_list = list()
                    for title in custom_list:
                        self.cursor.execute('SELECT ytb_code FROM archive '
                                            f'WHERE title={title}')
                        code_list.append('https://youtu.be/'
                                         f'{self.cursor.fetchall()[0]}')
                    custom_list = tuple(code_list)

                break

            elif option == '':
                if playlist == 'playlist':
                    self.cursor.execute('SELECT title FROM active')
                    custom_list = tuple([f'"{title[0]}"*' for title
                                         in self.cursor.fetchall()])
                else:
                    self.cursor.execute('SELECT ytb_code FROM archive')
                    custom_list = tuple([f'https://youtu.be/{code[0]}' for
                                        code in self.cursor.fetchall()])
                break

            else:
                try:
                    music_id = int(option)
                except ValueError:
                    continue

                if playlist == 'playlist':
                    self.cursor.execute('SELECT title FROM active '
                                        f'WHERE music_id={music_id}')
                    custom_list = tuple([f'"{title[0]}"*' for title
                                         in self.cursor.fetchall()])
                else:
                    self.cursor.execute('SELECT ytb_code FROM archive '
                                        f'WHERE music_id={music_id}')
                    custom_list = tuple([f'https://youtu.be/{code[0]}' for
                                        code in self.cursor.fetchall()])
                break

        cmd = 'mpv '
        if playlist == 'playlist':
            os.chdir(self.music_path)
        else:
            cmd += '--no-video '
        if len(custom_list) == 0:
            print('Error: Selection has no music entries...')
            return
        elif len(custom_list) > 1:
            if input(':: Play it randomly or in order? [R/o] ').lower() \
                    in ('', 'o'):
                cmd += '--shuffle '
        cmd += ' '.join(custom_list)
        subprocess.run(cmd, shell=True)
        pass

    def add(self):
        pass

    def remove(self):
        pass

    def recover_arc(self):
        pass

    def edit(self):
        pass

    @generic_connection
    def show(self, playlist, mode):
        table = 'active' if playlist == 'playlist' else 'archive'
        selection = '*' if mode == 'all' else 'music_id, title'

        df = pd.read_sql(f'SELECT {selection} FROM {table} ORDER BY music_id',
                         self.db_con)
        if len(df) == 0:
            print(f'{playlist.capitalize()} is empty...')
            return

        print(df.to_string(index=False))

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
