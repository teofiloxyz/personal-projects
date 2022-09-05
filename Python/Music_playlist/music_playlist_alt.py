#!/usr/bin/python3
# MusicPlaylist menu com diversas funções, versão alternativa
# NEEDS LOTS OF REFACTORING

import os
import subprocess
import sqlite3
import pandas as pd
from datetime import datetime
from Tfuncs import gmenu, inpt, oupt
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

    def search(self, table, query=None):
        while True:
            if query is None:
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
                query = None
                continue
            else:
                return result

    @generic_connection
    def play(self, playlist):
        while True:
            print(f'\nls: Show {playlist} titles\ng: Search by genre\n'
                  '#: Play music with # ID\n')
            option = input('Pick one of the options above '
                           f'or leave empty to play the whole {playlist}\n'
                           'Anything else will do a search: ')

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
                    table = 'active' if playlist == 'playlist' else 'archive'
                    custom_list = self.search(table, query=option)
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
                                                f'WHERE title="{title}"')
                            code_list.append('https://youtu.be/'
                                             f'{self.cursor.fetchall()[0][0]}')
                        custom_list = tuple(code_list)

                    break

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

    @generic_connection
    def add(self, playlist, entry=None, ytb_code=None):
        table = 'active' if playlist == 'playlist' else 'archive'
        if entry is None:
            now = datetime.now().strftime("%Y-%m-%d %H:%M")

            if ytb_code is None:
                ytb_code = input('Enter the youtube link or video code: ')
            if ytb_code == 'q':
                print('Aborted...')
                return
            elif '/' in ytb_code:
                ytb_code = ytb_code.split('/')[-1]
            self.cursor.execute(f'SELECT * FROM {table} '
                                f'WHERE ytb_code="{ytb_code}"')
            if self.cursor.fetchone() is not None:
                print(f'Already have that youtube code on the {playlist}')
                return
            ytb_link = 'https://youtu.be/' + ytb_code

            print("Getting title...")
            cmd = f'yt-dlp --get-title {ytb_link}'.split()
            title = subprocess.run(cmd, capture_output=True) \
                .stdout.decode('utf-8')[:-1]
            if title.startswith('ERROR:') or title == '':
                print("Problem getting title...\nAborting...")
                return
            custom_title = input('Enter custom title (artist - song) '
                                 f'or leave empty for "{title}": ')
            if custom_title == 'q':
                print('Aborted...')
                return
            elif custom_title != '':
                title = custom_title
            title = title.replace('"', "'")
            title = title.replace(',', " ")
            title = title.replace('/', "|")
            self.cursor.execute(f'SELECT title FROM {table}')
            titles = tuple([f'{title[0]}' for title
                            in self.cursor.fetchall()])
            while title in titles:
                print(f'Title: "{title}" already exists!')
                title = input('Enter custom title (artist - song): ')
                if title == 'q':
                    print('Aborted...')
                    return
                title = title.replace('"', "'")
                title = title.replace(',', " ")
                title = title.replace('/', "|")

            self.cursor.execute('SELECT genre FROM genres')
            genres = tuple([genre[0] for genre in self.cursor.fetchall()])
            if len(genres) == 0:
                qst = 'Enter the genre(s) (e.g.: Rock; Pop+Rock): '
            else:
                [print(f'[{n}] {genre}') for n, genre in enumerate(genres, 1)]
                qst = 'Enter the genre(s) number(s) (e.g.: 2; 4+2+3)\nOr ' \
                    'enter a custom genre(s) (e.g.: Rock; Pop+Rock; 3+Pop+1): '
            ans = input(qst)
            if ans == 'q':
                print('Aborted...')
                return
            ans_list = ans.split('+')
            genre = []
            for ans in ans_list:
                try:
                    genre.append(genres[int(ans) - 1])
                except (ValueError, IndexError):
                    # Custom genre
                    genre.append(ans.capitalize())
                    self.cursor.execute('INSERT INTO genres (genre) '
                                        f'VALUES ({genre})')
                    self.db_con.commit()

            genre = '|'.join(genre)

            entry = now, title, ytb_code, genre
        else:
            title, ytb_code = entry[1], entry[2]
            self.cursor.execute(f'SELECT * FROM {table} '
                                f'WHERE ytb_code="{ytb_code}"')
            if self.cursor.fetchone() is not None:
                print(f'Already have that youtube code on the {playlist}')
                return

        if playlist == 'playlist':
            ytb_link = 'https://youtu.be/' + ytb_code
            print("Downloading...")
            cmd = 'yt-dlp -f "bestaudio" --continue --no-overwrites ' \
                '--ignore-errors --extract-audio ' \
                f'-o "{self.music_path}/{title}.%(ext)s" {ytb_link}'
            err = subprocess.call(cmd, shell=True, stdout=subprocess.DEVNULL)
            if err != 0:
                print('Error downloading...\nAborting...')
                return

        self.cursor.execute(f'INSERT INTO {table} (date_added, title, '
                            f'ytb_code, genre) VALUES {entry}')
        self.db_con.commit()
        print(f'"{title}" added to the {playlist}!')

    @generic_connection
    def remove(self, playlist, ytb_code=None):
        table = 'active' if playlist == 'playlist' else 'archive'
        if ytb_code is None:
            while True:
                print(f'\nls: Show {playlist} titles\n'
                      's: Search by title\n#: Choose music with # ID')
                option = input('Pick one of the options above: ')

                if option == 'q':
                    print('Aborted...')
                    return

                elif option == 'ls':
                    self.show(playlist, 'titles')
                    # need to connect db again, bc show func closes database
                    self.db_con = sqlite3.connect(self.db_path)
                    self.cursor = self.db_con.cursor()

                elif option == 's':
                    table = 'active' if playlist == 'playlist' else 'archive'
                    custom_list = self.search(table)
                    if custom_list == 'q':
                        return
                    elif len(custom_list) > 1:
                        [print(f'[{n}] {title}')
                         for n, title in enumerate(custom_list, 1)]
                        selected_title = input('Enter the title number'
                                               '(e.g: 2): ')
                        try:
                            selected_title = (custom_list
                                              [int(selected_title) - 1])
                        except (ValueError, IndexError):
                            print('Aborted...')
                            return
                    else:
                        selected_title = custom_list[0]

                    self.cursor.execute(f'SELECT ytb_code FROM {table} '
                                        f'WHERE title="{selected_title}"')
                    ytb_code = self.cursor.fetchone()[0]
                    break

                else:
                    try:
                        music_id = int(option)
                    except ValueError:
                        continue

                    self.cursor.execute(f'SELECT ytb_code FROM {table} '
                                        f'WHERE music_id={music_id}')
                    ytb_code = self.cursor.fetchone()
                    if ytb_code is None:
                        print(f"Entry not found with ID {music_id}")
                        continue
                    else:
                        ytb_code = ytb_code[0]
                    break

        self.cursor.execute(f'SELECT * FROM {table} '
                            f'WHERE ytb_code="{ytb_code}"')
        entry = self.cursor.fetchone()[1:]
        self.cursor.execute(f'DELETE FROM {table} WHERE ytb_code="{ytb_code}"')
        self.db_con.commit()
        print(f'"{entry[1]}" removed from the {playlist}!')

        if playlist == 'playlist':
            # fiz assim por causa da extensão ñ estar no título; melhorar
            music_file = None
            for file in os.listdir(self.music_path):
                if file.startswith(entry[1]):
                    music_file = os.path.join(self.music_path, file)
                    break
            if music_file is not None:
                os.remove(music_file)
            else:
                print("WARNING! Didn't find associated music file... "
                      "Assuming it's already removed")

            self.add('archive', entry=entry)

    @generic_connection
    def recover_arc(self):
        while True:
            print('\nls: Show archive titles\n'
                  's: Search by title\n#: Choose music with # ID')
            option = input('Pick one of the options above: ')

            if option == 'q':
                print('Aborted...')
                return

            elif option == 'ls':
                self.show('archive', 'titles')
                # need to connect db again, bc show func closes database
                self.db_con = sqlite3.connect(self.db_path)
                self.cursor = self.db_con.cursor()

            elif option == 's':
                custom_list = self.search('archive')
                if custom_list == 'q':
                    return
                elif len(custom_list) > 1:
                    [print(f'[{n}] {title}')
                     for n, title in enumerate(custom_list, 1)]
                    selected_title = input('Enter the title number'
                                           '(e.g: 2): ')
                    try:
                        selected_title = (custom_list
                                          [int(selected_title) - 1])
                    except (ValueError, IndexError):
                        print('Aborted...')
                        return
                else:
                    selected_title = custom_list[0]

                self.cursor.execute('SELECT * FROM archive '
                                    f'WHERE title="{selected_title}"')
                entry = self.cursor.fetchone()[1:]
                break

            else:
                try:
                    music_id = int(option)
                except ValueError:
                    continue

                self.cursor.execute(f'SELECT * FROM archive '
                                    f'WHERE music_id={music_id}')
                entry = self.cursor.fetchone()[1:]
                if entry is None:
                    print(f"Entry not found with ID {music_id}")
                    continue
                break

        self.remove('archive', entry[2])
        self.add('playlist', entry)

    @generic_connection
    def edit(self, playlist):
        table = 'active' if playlist == 'playlist' else 'archive'
        while True:
            print(f'\nls: Show {playlist} titles\n'
                  's: Search by title\n#: Choose music with # ID')
            option = input('Pick one of the options above: ')
            if option == 'q':
                print('Aborted...')
                return
            elif option == 'ls':
                self.show(playlist, 'titles')
                # need to connect db again, bc show func closes database
                self.db_con = sqlite3.connect(self.db_path)
                self.cursor = self.db_con.cursor()
            elif option == 's':
                custom_list = self.search(table)
                if custom_list == 'q':
                    return
                elif len(custom_list) > 1:
                    [print(f'[{n}] {title}')
                     for n, title in enumerate(custom_list, 1)]
                    selected_title = input('Enter the title number'
                                           '(e.g: 2): ')
                    try:
                        selected_title = (custom_list
                                          [int(selected_title) - 1])
                    except (ValueError, IndexError):
                        print('Aborted...')
                        return
                else:
                    selected_title = custom_list[0]
                self.cursor.execute(f'SELECT ytb_code FROM {table} '
                                    f'WHERE title="{selected_title}"')
                ytb_code = self.cursor.fetchone()[0]
                break
            else:
                try:
                    music_id = int(option)
                except ValueError:
                    continue
                self.cursor.execute(f'SELECT ytb_code FROM {table} '
                                    f'WHERE music_id={music_id}')
                ytb_code = self.cursor.fetchone()
                if ytb_code is None:
                    print(f"Entry not found with ID {music_id}")
                    continue
                else:
                    ytb_code = ytb_code[0]
                break

        option = input('Edit [t]itle or [g]enre? ')
        if option.lower() == 't':
            self.cursor.execute(f'SELECT title FROM {table} '
                                f'WHERE ytb_code="{ytb_code}"')
            title = self.cursor.fetchone()[0]
            print(f"Current title: {title}")

            new_title = input("Enter the new title: ")
            if new_title == 'q':
                print('Aborted...')
                return
            new_title = new_title.replace('"', "'")
            new_title = new_title.replace(',', " ")
            new_title = new_title.replace('/', "|")
            self.cursor.execute(f'UPDATE {table} SET title="{new_title}"'
                                f'WHERE ytb_code="{ytb_code}"')
            self.db_con.commit()
            if playlist == 'playlist':
                tracks = os.listdir(self.music_path)
                for track in tracks:
                    if track.startswith(title):
                        extension = os.path.splitext(track)[-1]
                        break
                os.rename(self.music_path + '/' + title + extension,
                          self.music_path + '/' + new_title + extension)
            print(f'Title changed from "{title}" to "{new_title}"')

        elif option.lower() == 'g':
            self.cursor.execute(f'SELECT genre FROM {table} '
                                f'WHERE ytb_code="{ytb_code}"')
            genre = self.cursor.fetchone()[0]
            print(f"Current genre: {genre}")

            self.cursor.execute('SELECT genre FROM genres')
            genres = tuple([genre[0] for genre in self.cursor.fetchall()])
            if len(genres) == 0:
                qst = 'Enter the genre(s) (e.g.: Rock; Pop+Rock): '
            else:
                [print(f'[{n}] {genre}')
                 for n, genre in enumerate(genres, 1)]
                qst = 'Enter the genre(s) number(s) (e.g.: 2; 4+2+3)\n' \
                    'Or enter a custom genre(s) (e.g.: Rock; Pop+Rock; ' \
                    '3+Pop+1): '
            ans = input(qst)
            if ans == 'q':
                print('Aborted...')
                return
            ans_list = ans.split('+')
            new_genre = []
            for ans in ans_list:
                try:
                    new_genre.append(genres[int(ans) - 1])
                except (ValueError, IndexError):
                    # Custom genre
                    new_genre.append(ans.capitalize())
                    self.cursor.execute('INSERT INTO genres (genre) '
                                        f'VALUES ({new_genre})')
                    self.db_con.commit()

            new_genre = '|'.join(new_genre)
            self.cursor.execute(f'UPDATE {table} SET genre="{new_genre}"'
                                f'WHERE ytb_code="{ytb_code}"')
            self.db_con.commit()
            print(f'Genre changed from "{genre}" to "{new_genre}"')

        else:
            print('Aborted...')

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

    def download(self):
        def download(link, mp3):
            cmd = 'yt-dlp -f "bestaudio" --continue --no-overwrites ' \
                  '--ignore-errors --extract-audio ' \
                  f'-o "{output_path}%(title)s.%(ext)s" {link}'
            if mp3:
                cmd += " --audio-format mp3"
            subprocess.run(cmd, shell=True)

        def check_if_link(entry):
            if '/' not in entry:
                return False
            code = str(entry).split('/')[-1]  # str é devido ao IDE
            if len(code) == 11 and ' ' not in code:
                return 'https://youtu.be/' + code
            else:
                return False

        def get_link(title):
            search = YoutubeSearch(str(title), max_results=1).to_dict()
            return f'https://youtu.be/{search[0]["id"]}'

        from youtube_search import YoutubeSearch
        txt = inpt.files(question='Enter the txt file full path: ',
                         extensions='txt')
        output_path = self.downloads_path
        if not os.path.exists(output_path):
            os.makedirs(output_path, exist_ok=True)

        if input(":: Want output format to be mp3? [y/N] ").lower() == 'y':
            mp3 = True
        else:
            mp3 = False

        with open(str(txt), 'r') as tx:
            entries = tx.readlines()
        for entry in entries:
            entry = entry.strip('\n')
            if entry.strip(' ') == '':
                continue
            link = check_if_link(entry)
            if link is False:
                link = get_link(entry)
            download(link, mp3)

    @generic_connection
    def export_csv(self):
        playlist = input('Choose [p]laylist or [a]rchive to export: ')
        if playlist == 'p':
            table = 'active'
        elif playlist == 'a':
            table = 'archive'
        else:
            print('Aborted...')
            return

        csv_output = oupt.files('Enter csv output path: ', extension='csv',
                                output_name=f'music_playlist_{table}')
        if csv_output == 'q':
            print('Aborted...')
            return

        df = pd.read_sql('SELECT date_added, title, ytb_code, genre '
                         f'FROM {table}', self.db_con)
        df.to_csv(str(csv_output), encoding='utf-8', index=False)

        if os.path.isfile(csv_output):
            print(f"Export done successfuly\nOutput at '{csv_output}'")
        else:
            print('Error, something went wrong exporting to CSV')

    def import_csv(self):
        playlist = input('Choose [p]laylist or [a]rchive to export: ')
        if playlist == 'p':
            playlist, table = 'playlist', 'active'
        elif playlist == 'a':
            playlist, table = 'archive', 'archive'
        else:
            print('Aborted...')
            return

        csv_input = inpt.files('Enter csv input path: ', extensions='csv')
        if csv_input == 'q':
            print('Aborted...')
            return

        with open(csv_input, 'r') as cs:
            lines = cs.readlines()

        header = 'date_added,title,ytb_code,genre'
        header2 = 'title,ytb_code,genre'
        if lines[0].strip('\n') not in (header, header2):
            print(f'Csv header must be: {header} or {header2}')
            return

        self.cursor.execute(f'DROP TABLE {table}')
        self.db_con.commit()
        self.cursor.execute(f'CREATE TABLE {table}(music_id '
                            'INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL '
                            'UNIQUE, date_added TEXT NOT NULL, title TEXT '
                            'NOT NULL UNIQUE, ytb_code TEXT NOT NULL UNIQUE, '
                            'genre TEXT NOT NULL)')
        self.db_con.commit()
        lines = lines[1:]
        if lines[0].strip('\n') == header2:
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            for line in lines:
                line = line.strip('\n').split(',')
                entry = now, line[0], line[1], line[2]
                self.add(playlist, entry)
        else:
            for line in lines:
                line = line.strip('\n').split(',')
                entry = line[0], line[1], line[2], line[3]
                self.add(playlist, entry)

        print('Import done!')

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
            'd': (pl.download,
                  "Download from txt file with titles and/or links"),
            'xc': (pl.export_csv,
                   "Export playlist (or archive) to CSV"),
            'ic': (pl.import_csv,
                   "Import playlist (or archive) from CSV")}
    gmenu(title, keys)
