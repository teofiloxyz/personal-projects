#!/usr/bin/python3

import os
import sys
from configparser import ConfigParser
from Tfuncs import rofi


class Code:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read('config.ini')
        self.python_path = self.config['CODE']['python_path']
        self.bash_path = self.config['CODE']['bash_path']

    def main(self, code_type, entry):
        if code_type == 'python':
            self.dir_path = self.python_path
            self.extension = '.py'
            print('Searching in all .py files\n')
        else:
            self.dir_path = self.bash_path
            self.extension = '.sh'
            print('Searching in all .sh files\n')

        self.entry = entry
        self.get_files_list()

        if self.search_entry():
            self.rofi_dmenu()
            if self.choice != "":
                self.open_choice()

    def get_files_list(self):
        # follow links only if in bash (old scripts)
        if self.extension == '.sh':
            links = True
        else:
            links = False

        self.files_list = [os.path.join(root_dirs_files[0], file)
                           for root_dirs_files
                           in os.walk(self.dir_path, followlinks=links)
                           for file in root_dirs_files[2]
                           if file.endswith(self.extension)]

    def search_entry(self):
        self.results, rs_lines, rs_files, n = {}, [], [], 1
        for file in self.files_list:
            with open(file, 'r') as cf:
                cf_lines = cf.readlines()
            for line in cf_lines:
                if self.entry.lower() in line.lower():
                    line_num = cf_lines.index(line) + 1
                    line = ' '.join(line.split())
                    if not (line in rs_lines and file in rs_files):
                        rs_files.append(file)
                        rs_lines.append(line)
                        self.results[str(n)] = (line, file, line_num)
                        n += 1

        if len(self.results) == 0:
            rofi.message(f"Didn't find any line of code with '{self.entry}'")
            return False
        return True

    def rofi_dmenu(self):
        prompt = 'Choose which one to open'
        dmenu = [f"{result[0]} -> {os.path.basename(result[1])}: {result[2]}"
                 for result in self.results.values()]
        self.choice = rofi.custom_dmenu(prompt, dmenu)

    def open_choice(self):
        line, file = self.choice.split(" -> ")[-2], ""
        file_basename, line_num = self.choice.split(" -> ")[-1].split(": ")
        for result in self.results.values():
            if result[0] == line and result[1].endswith(file_basename) \
                    and str(result[2]) == line_num:
                file = result[1]
                break
        os.system(f'alacritty -e nvim +{line_num} {file}')


if len(sys.argv) > 2:
    code_type = sys.argv[1]
    entry = ' '.join(sys.argv[2:])
    Code().main(code_type, entry)
else:
    print('Argument needed...')
