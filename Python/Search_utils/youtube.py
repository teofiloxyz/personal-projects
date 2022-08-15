#!/usr/bin/python3

import sys
import subprocess
import time
from configparser import ConfigParser
from youtube_search import YoutubeSearch


class Youtube:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read('config.ini')
        self.music_playlist = self.config['YOUTUBE']['music_playlist']
        self.download_path = self.config['YOUTUBE']['download_path']
        self.max_results = 15

    def main(self, entry):
        self.entry = entry
        self.search()

    def search(self):
        print(f"\nSearching on youtube for '{self.entry}':")
        results = YoutubeSearch(str(self.entry),
                                max_results=self.max_results).to_dict()

        self.links = []
        for n, result in enumerate(results, 1):
            print(f'[{n}] {result["title"]}')
            self.links.append(f'https://youtu.be/{result["id"]}')

        while True:
            self.link_num = input('\nChoose title or search another video: ')
            try:
                self.link_num = int(self.link_num)
                if 1 <= self.link_num <= (len(results)):
                    self.play()
                    return
                else:
                    print('Wrong number!')
            except ValueError:
                if self.link_num == 'q':
                    print('Aborted...')
                    return
                self.entry = self.link_num
                self.search()
                return

    def play(self):
        self.link = self.links[int(self.link_num) - 1]
        while True:
            mode = input(":: Sound, video or menu (won't close)? [S/v/m] ")
            if mode == 'q':
                print('Aborted...')
                return
            elif mode.lower() in ('', 's'):
                subprocess.run(['mpv', self.link, '--no-video'])
                return
            elif mode.lower() == 'v':
                subprocess.run(['mpv', self.link])
                return
            elif mode.lower() == 'm':
                self.menu()
                return

    def menu(self):
        sys.path.insert(0, self.music_playlist)
        from music_playlist import MusicPlaylist

        print('\nMenu mode')
        while True:
            mode = input(':: Sound or video? [S/v] ')
            if mode == 'q':
                print('Aborted...')
                return
            elif mode.lower() in ('', 's'):
                subprocess.run(['mpv', self.link, '--no-video'])
                break
            elif mode.lower() == 'v':
                subprocess.run(['mpv', self.link])
                break

        menu_ans = input('\nEnter another search\nOr press <enter> for same\n'
                         'Or [a]dd to playlist\nOr [d]ownload: ')
        if menu_ans == 'a':
            MusicPlaylist().add('playlist', link=self.link)
            time.sleep(2)

        elif menu_ans == 'd':
            cmd = 'yt-dlp -f "bestaudio" --continue --no-overwrites ' \
                '--ignore-errors --extract-audio ' \
                f'-o "{self.download_path}/%(title)s.%(ext)s" {self.link}'
            err = subprocess.call(cmd, shell=True, stdout=subprocess.DEVNULL)
            if err != 0:
                print('Error downloading...\nAborting...')
                return
            else:
                print(f"Download at {self.download_path}")
            time.sleep(2)

        elif menu_ans == '':
            self.search()
        else:
            self.entry = menu_ans
            self.search()


if len(sys.argv) > 1:
    entry = ' '.join(sys.argv[1:])
    Youtube().main(entry)
else:
    print('Argument needed...')
