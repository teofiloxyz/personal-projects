#!/usr/bin/python3

import sys
import subprocess
from configparser import ConfigParser


class Browser:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read('config.ini')
        self.browser = self.config['BROWSER']['browser']
        self.search_engine = self.config['BROWSER']['search_engine']

    def main(self, search_type, entry):
        # Add whatever you want
        options = {'s': '',
                   'p': 'python ',
                   'b': 'bash ',
                   'g': 'golang ',
                   'la': 'latex ',
                   'l': 'linux '}
        option = options[search_type]

        search_url = option + entry
        search_url = search_url.replace(' ', '+')

        cmd = f'{self.browser} --new-tab --url ' \
              f'{self.search_engine}{search_url}'
        subprocess.Popen(cmd, shell=True, start_new_session=True)


if len(sys.argv) > 2:
    search_type = sys.argv[1]
    entry = ' '.join(sys.argv[2:])
    Browser().main(search_type, entry)
else:
    print('Argument needed...')
