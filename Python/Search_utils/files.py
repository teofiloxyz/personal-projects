#!/usr/bin/python3
# Search file or folder by title

import os
import sys
import subprocess
from Tfuncs import rofi


class Files:
    def __init__(self):
        self.dir_path = '/home'

    def main(self, entry):
        self.entry = entry
        if self.search_entry():
            self.rofi_dmenu()
            if self.choice != "":
                self.open_choice()

    def search_entry(self):
        cmd = f'fd --hidden --ignore-case "{self.entry}" {self.dir_path}'
        self.results = subprocess.run(cmd, shell=True, capture_output=True) \
            .stdout.decode('utf-8').split('\n')[:-1]

        if len(self.results) == 0:
            rofi.message(f"Didn't find in home any file with '{self.entry}'")
            return False
        return True

    def rofi_dmenu(self):
        prompt = 'Choose which one to open with ranger'
        dmenu = self.results
        self.choice = rofi.custom_dmenu(prompt, dmenu)
        if not os.path.isdir(self.choice):
            self.choice = os.path.dirname(self.choice)

    def open_choice(self):
        cmd = f'alacritty -e ranger "{self.choice}"'
        subprocess.run(cmd, shell=True)


if len(sys.argv) > 1:
    entry = ' '.join(sys.argv[1:])
    Files().main(entry)
else:
    print('Argument needed...')
