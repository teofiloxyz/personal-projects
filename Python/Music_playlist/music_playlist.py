#!/usr/bin/python3
# MusicPlaylist menu com diversas funções

import os
import sys
import subprocess
import pickle
from datetime import datetime
from configparser import ConfigParser
from Tfuncs import gmenu, inpt, oupt


class MusicPlaylist:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read('config.ini')
        self.playlist_path = self.config['GENERAL']['playlist_path']
        self.arc_path = self.config['GENERAL']['archive_path']
        self.playlist_txt_path = self.config['GENERAL']['playlist_txt_path']
        self.search_utils_path = self.config['GENERAL']['search_utils_path']
        self.downloads_path = self.config['GENERAL']['downloads_path']

        self.load('playlist')
        self.load('archive')

    def play(self, playlist, entries=None):
        def play(mode, txt=None, random=False):
            if mode == 'entire':
                print(f"\nPlaying from '{playlist.capitalize()}'")
                cmd = f'mpv --playlist={txt} --no-video'
                if random:
                    cmd += ' --shuffle'
            elif mode == 'single':
                print(f"\nPlaying '{title}'")
                cmd = f'mpv {self.link} --no-video'
            subprocess.run(cmd, shell=True)

        if playlist in ('playlist', 'archive'):
            if playlist == 'playlist':
                entries, genres = self.pl_entries, self.pl_genres
            else:
                entries, genres = self.arc_entries, self.arc_genres
            self.show(playlist, 'titles')
            option = input('\nPick the list ID of the music to play\n'
                           f'Or leave empty to play the whole {playlist}\n'
                           'Or enter [g] to play all by genre: ')
        else:
            option = ''

        if option == 'q':
            print('Aborted...')
            return

        elif option == '':
            txt = '/tmp/quick_music_playlist.txt'
            self.create_playlist_txt(txt, entries)
            option = input(':: Play it in order or random? [O/r] ')
            if option.lower() in ('', 'o'):
                play('entire', txt)
            elif option.lower() == 'r':
                play('entire', txt, random=True)
            else:
                print('Aborted...')
                return False

        elif option == 'g':
            [print(f'[{n}] {genre}') for n, genre in enumerate(genres, 1)]
            selected_genres = input('Enter the genre number or combo '
                                    '(e.g: 2; 4+2+3): ')
            selected_genres_list = []
            for genre in selected_genres.split('+'):
                try:
                    selected_genres_list.append(genres[int(genre) - 1])
                except (ValueError, IndexError):
                    print('Aborted...')
                    return

            selected_genres_entries = {}
            for link, val in entries.items():
                for genre in selected_genres_list:
                    if genre in val[1]:
                        selected_genres_entries[link] = val
                        break

            playlist += f": {' + '.join(selected_genres_list)}"
            self.play(playlist, entries=selected_genres_entries)

        else:
            self.link = option
            if self.check_ls_id(entries) is False:
                return
            title = entries[self.link][0]
            play('single')

    def add(self, playlist, link=None, title=False, genre=False):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        if link is not None:
            self.link = link

        if self.check_link('add', playlist, link) is False:
            return

        if not title:
            cmd = f'yt-dlp --get-title {self.link}'.split()
            self.title = subprocess.run(cmd, capture_output=True) \
                .stdout.decode('utf-8')[:-1]
            if title is None or title == '':
                print('Error: could not get title of link')
                self.title = input('Please enter the title (artist - song): ')
                if self.title == 'q':
                    print('Aborted...')
                    return

        if not genre:
            genres = self.pl_genres if playlist == 'playlist' \
                else self.arc_genres
            [print(f'[{n}] {genre}') for n, genre in enumerate(genres, 1)]
            if len(genres) == 0:
                qst = 'Enter the genre(s) (e.g.: Rock; Pop+Rock): '
            else:
                qst = 'Enter the genre(s) number(s) (e.g: 2; 4+2+3)\nOr ' \
                    'enter a custom genre(s) (e.g.: Rock; Pop+Rock; 3+Pop+1): '
            genre = input(qst)
            if genre == 'q':
                print('Aborted...')
                return

            self.genre = []
            for gen in genre.split('+'):
                try:
                    self.genre.append(genres[int(gen) - 1])
                except (ValueError, IndexError):
                    self.genre.append(gen)
            self.genre = tuple(self.genre)

        if playlist == 'playlist':
            self.pl_entries[self.link] = (self.title, self.genre, now)
        else:
            self.arc_entries[self.link] = (self.title, self.genre, now)

        self.save(playlist)
        print(f"'{self.title}' added to the {playlist}!")

    def remove(self, playlist, link=None):
        if link is not None:
            self.link = link

        if self.check_link('remove', playlist, link) is False:
            return

        if playlist == 'playlist':
            self.title = self.pl_entries[self.link][0]
            self.genre = self.pl_entries[self.link][1]
            self.add('archive', link=self.link, title=True, genre=True)
            self.pl_entries.pop(self.link)
        else:
            self.title = self.arc_entries[self.link][0]
            self.genre = self.arc_entries[self.link][1]
            self.arc_entries.pop(self.link)

        self.save(playlist)
        print(f"'{self.title}' removed from the {playlist}!")

    def recover_arc(self, link=None):
        if link is not None:
            self.link = link
        else:
            if self.check_link('recover', 'archive') is False:
                return

        self.remove('archive', self.link)
        self.add('playlist', self.link, title=True, genre=True)

    def show(self, playlist, mode):
        def show_titles():
            [print(f'[{n}]\t{title[0]}')
                for n, title in enumerate(entries.values(), 1)]

        def show_all():
            [print(f'[{n}]\t{link}\t{entries[link][2]}\t'
                   f'{", ".join(entries[link][1])}\n{entries[link][0]}\n\n')
             for n, link in enumerate(entries.keys(), 1)]

        entries = \
            self.pl_entries if playlist == 'playlist' else self.arc_entries

        if len(entries) == 0:
            print(f'{playlist.capitalize()} is empty...')
            return

        if mode == 'titles':
            show_titles()
        elif mode == 'all':
            show_all()

    def youtube_search(self):
        sys.path.insert(0, self.search_utils_path)
        from youtube import Youtube

        entry = input('Enter the title to search on youtube: ')
        if entry == 'q':
            print('Aborted...')
            return
        Youtube().main(entry)

    def search(self, playlist):
        def change_title(link):
            title, genre, date_added = entries[link]
            new_title = input(f"Current title is '{title}'"
                              "\nEnter new title: ")
            if new_title == 'q':
                print('Aborted...')
                return

            if playlist == 'playlist':
                self.pl_entries[link] = (new_title, genre, date_added)
            else:
                self.arc_entries[link] = (new_title, genre, date_added)

            self.save(playlist)
            print(f"Title changed to {new_title}")

        def change_genre(link):
            title, old_genre, date_added = entries[link]
            old_genre = "' , '".join(old_genre)
            genres = self.pl_genres if playlist == 'playlist' \
                else self.arc_genres
            [print(f'[{n}] {genre}') for n, genre in enumerate(genres, 1)]
            print(f"\nCurrent genre is '{old_genre}'")
            new_genre = input('Enter the genre number (e.g: 2; 4+2+3)\n'
                              'Or enter a custom genre '
                              '(e.g.: Rock; Pop+Rock; 3+Pop+1): ')

            if new_genre == 'q':
                print('Aborted...')
                return
            else:
                genre = []
                for gen in new_genre.split('+'):
                    try:
                        genre.append(genres[int(gen) - 1])
                    except (ValueError, IndexError):
                        genre.append(gen)
            new_genre = tuple(genre)

            if playlist == 'playlist':
                self.pl_entries[link] = (title, new_genre, date_added)
            else:
                self.arc_entries[link] = (title, new_genre, date_added)

            self.save(playlist)
            print(f"Genre changed to {new_genre}")

        entries = self.pl_entries if playlist == 'playlist' \
            else self.arc_entries

        query = input('Enter music title to search: ').split()
        if query[0] == 'q':
            print('Aborted...')
            return

        if len(query) == 1:
            results = {link: title[0] for link, title in entries.items()
                       if query[0].lower() in title[0].lower()}
        else:
            results = {}
            for link, title in entries.items():
                does_match = True
                for word in query:
                    if word.lower() not in title[0].lower():
                        does_match = False
                        break
                if does_match:
                    results[link] = title[0]

        if len(results) == 0:
            query = "' and '".join(query)
            print(f"Nothing was found with '{query}' "
                  "on the title")
            return

        links = list(results.keys())
        [print(f'[{n}]\t{title}')
         for n, title in enumerate(results.values(), 1)]

        while True:
            if len(links) == 1:
                title_index = None
                self.link = links[0]
                self.title = results[self.link]
                break

            title_index = input('\nChoose the title, or leave empty '
                                'to choose all results: ')
            if title_index == 'q':
                print('Aborted...')
                return
            elif title_index == '':
                self.title = 'All results'
                break
            else:
                try:
                    title_index = int(title_index) - 1
                    self.link = links[title_index]
                    self.title = results[self.link]
                    break
                except (ValueError, IndexError):
                    print('Invalid answer...')

        if playlist == 'playlist':
            option = input(":: Play, Remove, Download, change title "
                           f"or change genre of '{self.title}'? [P/r/d/t/g] ")
        else:
            option = input(":: Play, Remove, Recover, Download, change title "
                           f"or change genre of '{self.title}'? "
                           "[P/r/rc/d/t/g] ")

        if option.lower() in ('', 'p'):
            if title_index == '':
                if self.play(playlist=self.title, entries=results) is False:
                    return
            else:
                print(f"Playing '{self.title}'")
                cmd = f'mpv {self.link} --no-video'
                subprocess.run(cmd, shell=True)

        elif option.lower() == 'r':
            if title_index != '':
                self.remove(playlist, link=self.link)
            else:
                [self.remove(playlist, link=link) for link in results.keys()]

        elif option.lower() == 'rc' and playlist == 'archive':
            if title_index != '':
                self.recover_arc(self.link)
            else:
                [self.recover_arc(link) for link in results.keys()]

        elif option.lower() == 'd':
            if title_index != '':
                self.download('single', link=self.link)
            else:
                [self.download('youtube', link=link)
                 for link in results.keys()]

        elif option.lower() == 't':
            if title_index != '':
                change_title(link=self.link)
            else:
                [change_title(link=link) for link in results.keys()]

        elif option.lower() == 'g':
            if title_index != '':
                change_genre(link=self.link)
            else:
                [change_genre(link=link) for link in results.keys()]

        else:
            print('Aborted...')
            return

    def download(self, mode, link=None):
        def download(link):
            cmd = 'yt-dlp -f "bestaudio" --continue --no-overwrites ' \
                  '--ignore-errors --extract-audio ' \
                  f'-o "{output_path}%(title)s.%(ext)s" {link}'
            # add to cmd "--audio-format mp3" if you want
            subprocess.run(cmd, shell=True)

        def single():
            print(f"Downloading '{self.title}'")
            download(self.link)

        def youtube():
            download(self.link)

        def playlist():
            if input(f':: Download the whole {mode}? [y/N] ') \
                    not in ('y', 'Y'):
                print('Aborted...')
                return

            entries = \
                self.pl_entries if mode == 'playlist' else self.arc_entries
            [download(link) for link in entries.keys()]

        def txt():
            from youtube_search import YoutubeSearch

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

            txt = inpt.files(question='Enter the txt file full path: ',
                             extensions='txt')
            with open(str(txt), 'r') as tx:
                entries = tx.readlines()
            for entry in entries:
                entry = entry.strip('\n')
                if entry.strip(' ') == '':
                    continue
                link = check_if_link(entry)
                if link is False:
                    link = get_link(entry)
                download(link)

        if link is not None:
            self.link = link

        output_path = f"{self.downloads_path}/Music/"
        if not os.path.exists(output_path):
            os.makedirs(output_path, exist_ok=True)

        modes = {'single': single,
                 'youtube': youtube,
                 'playlist': playlist,
                 'archive': playlist,
                 'txt': txt}
        modes[mode]()

    def export_csv(self):
        playlist = input('Choose [p]laylist or [a]rchive to export: ')
        if playlist == 'p':
            entries = self.pl_entries
        elif playlist == 'a':
            entries = self.arc_entries
        else:
            print('Aborted...')
            return

        csv_output = oupt.files('Enter csv output path: ', extension='csv')
        if csv_output == 'q':
            print('Aborted...')
            return

        header = ('link', 'title')
        entries_links = tuple(entries.keys())
        entries_titles, entries_genres, entries_date_added = [], [], []
        for value in entries.values():
            entries_titles.append(value[0])
            entries_genres.append(value[1])
            entries_date_added.append(value[2])

        with open(csv_output, 'w') as cs:
            header = 'link,title,genre,added on\n'
            cs.write(header)
            for n in range(len(entries_links)):
                link = entries_links[n]
                title = entries_titles[n].replace(',', '')
                genres = ';'.join(entries_genres[n])
                date_added = entries_date_added[n]
                line = f'{link},{title},{genres},{date_added}\n'
                cs.write(line)
        print('Done!')

    def import_csv(self):
        csv_input = inpt.files('Enter csv output path: ', extensions='csv')
        if csv_input == 'q':
            print('Aborted...')
            return

        with open(csv_input, 'r') as cs:
            lines = cs.readlines()

        header = 'link,title,genre\n'
        header2 = 'link,title,genre,added on\n'
        if lines[0] not in (header, header2):
            print(f'Csv header must be: {header}Or {header2}')
            return

        lines = lines[1:]
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        entries = {}
        for n, line in enumerate(lines, 2):
            columns = line.strip('\n').split(',')
            if len(columns) not in (3, 4):
                print(f'Csv file has a problem on line {n}')
                return
            link = columns[0]
            title = columns[1].replace('"', '')
            genre = tuple(columns[2].split(';'))
            if len(columns) == 3:
                date_added = now
            else:
                date_added = columns[3]
            entries[link] = (title, genre, date_added)

        playlist = input('Choose [p]laylist or [a]rchive '
                         'to replace from csv import: ')
        if playlist == 'p':
            self.pl_entries = entries
            self.save('playlist')
        elif playlist == 'a':
            self.arc_entries = entries
            self.save('archive')
        else:
            print('Aborted...')
            return
        print('Done!')

    def load(self, playlist):
        def load(playlist_path):
            try:
                with open(playlist_path, 'rb') as pl:
                    entries = pickle.load(pl)
                # tem de ser tuple devido ao index
                genres = tuple({gen if type(val[1]) is tuple else val[1]
                               for val in entries.values()
                               for gen in val[1]})
                return entries, genres
            except (FileNotFoundError, EOFError):
                return {}, {}

        if playlist == 'playlist':
            self.pl_entries, self.pl_genres = \
                load(self.playlist_path)
        else:
            self.arc_entries, self.arc_genres = \
                load(self.arc_path)

    def save(self, playlist):
        def save(entries, playlist_path):
            entries = dict(sorted(entries.items(), key=lambda val: val[1]))
            genres = tuple({gen if type(val[1]) is tuple else val[1]
                            for val in entries.values()
                            for gen in val[1]})
            with open(playlist_path, 'wb') as pl:
                pickle.dump(entries, pl)
            return entries, genres

        if playlist == 'playlist':
            self.pl_entries, self.pl_genres = \
                save(self.pl_entries, self.playlist_path)
            txt = self.playlist_txt_path
            self.create_playlist_txt(txt, self.pl_entries)
        else:
            self.arc_entries, self.arc_genres = \
                save(self.arc_entries, self.arc_path)

    def create_playlist_txt(self, txt_path, entries):
        lines = [f'{link}\t {title[0]}\n' if type(title) is tuple
                 else f'{link}\t {title}\n'
                 for link, title in entries.items()]
        with open(txt_path, 'w') as tx:
            tx.writelines(lines)

    def check_link(self, mode, playlist, link=None):
        def check_link():
            self.link = self.link.split('/')[-1]
            if len(self.link) == 11:
                self.link = 'https://youtu.be/' + self.link
            if not self.link.startswith('https://youtu.be/'):
                print('Error: the link must be a youtube link or at least a '
                      'video code...')
                return False
            if mode == 'add' and self.link in entries.keys():
                print(f'Error: the link is already in the {playlist}...')
                return False
            elif mode in ('remove', 'recover') \
                    and self.link not in entries.keys():
                print(f'Error: the link was not found in the {playlist}...')
                return False

        entries = \
            self.pl_entries if playlist == 'playlist' else self.arc_entries

        question = 'Type youtube link/code to add: ' if mode == 'add' \
            else f'Type youtube link/code or ls ID to {mode}: '
        while True:
            if link is None:
                self.link = input(question)
                if self.link == 'q':
                    print('Aborted...')
                    return False
            else:
                self.link = link

            if mode in ('remove', 'recover'):
                if self.check_ls_id(entries) is False:
                    if check_link() is False:
                        if link is not None:
                            return False
                        continue
                else:
                    break
            else:
                if check_link() is False:
                    if link is not None:
                        return False
                    continue
            break

    def check_ls_id(self, playlist):
        try:
            self.link = int(self.link) - 1
        except ValueError:
            return False
        else:
            if not 0 <= self.link < len(playlist.keys()):
                print('Invalid rowid, select one in the list')
                return False
            self.link = list(playlist.keys())[self.link]


if __name__ == "__main__":
    pl = MusicPlaylist()
    title = 'Music-Playlist-Menu'
    keys = {'p': (lambda: pl.play('playlist'),
                  "Play music from playlist"),
            'pa': (lambda: pl.play('archive'),
                   "Play music from archive"),
            'ad': (lambda: pl.add('playlist'),
                   "Add link to playlist"),
            'rm': (lambda: pl.remove('playlist'),
                   "Remove link from playlist that goes to archive"),
            'ada': (lambda: pl.add('archive'),
                    "Add link to archive"),
            'rma': (lambda: pl.remove('archive'),
                    "Remove link from archive"),
            'rc': (pl.recover_arc,
                   "Recover link from archive"),
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
            's': (lambda: pl.search('playlist'),
                  "Search music from the playlist to play, download, "
                  "remove (and archive) or change title (or genre)"),
            'sa': (lambda: pl.search('archive'),
                   "Search music from the archive to play, download, "
                   "recover, remove or change title (or genre)"),
            'd': (lambda: pl.download('playlist'),
                  "Download the entire playlist"),
            'da': (lambda: pl.download('archive'),
                   "Download the entire archive"),
            'df': (lambda: pl.download('txt'),
                   "Download from txt file with titles and/or links"),
            'xc': (pl.export_csv,
                   "Export playlist or archive to CSV"),
            'ic': (pl.import_csv,
                   "Import playlist or archive from CSV")}
    gmenu(title, keys)
