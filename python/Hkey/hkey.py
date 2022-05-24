#!/usr/bin/python3
'''Hkey (ou hotkey) atua como launcher (semelhante ao dmenu/rofi), através
da execução de comandos na shell. Este script podia ser substituido por
'bashrc aliases' no terminal, no entanto isso iria criar conflitos com comandos
da shell, dada a enorme diversidade de potenciais hotkeys.
Além das hkeys, existem as rkeys (ou reserved keys) que executam uma função
específica deste script. Em breve, o mesmo terá uma interface gráfica.
A versão princial está escrita em Go (Golang)'''

import subprocess
import json
from threading import Thread
from datetime import datetime
from configparser import ConfigParser


class Hkey:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read('config.ini')

        self.hkeys_path = self.config['GENERAL']['hkeys_path']
        try:
            with open(self.hkeys_path, 'r') as hk:
                self.hkeys = json.load(hk)
        except FileNotFoundError:
            self.hkeys = {}

        self.rkeys = {'ls': (self.show_hkeys,
                             ': show hotkeys list'),
                      'ad': (self.add_hkey,
                             ': add entry to hotkeys list'),
                      'rm': (self.remove_hkey,
                             ': remove entry from hotkeys list'),
                      'ed': (self.edit_hkey,
                             ': edit entry from hotkeys list'),
                      'hs': (self.history_menu,
                             ': go to history menu'),
                      'h': (lambda: print(self.help_dialog),
                            ': show help dialog'),
                      'q': (exit,
                            ': quit')}

        self.history_path = self.config['GENERAL']['history_path']
        self.help_dialog = ''.join([f"'{key}'{func[1]}\n"
                                    for key, func in self.rkeys.items()])

    def main(self):
        while True:
            self.hkey = input('Enter hkey: ')
            if ' ' in self.hkey:
                self.hkey, self.cmd_input = self.hkey.split(' ', 1)
                self.hkey += ' '
                if self.cmd_input.replace(' ', '') == '':
                    print('Input must be something...\n')
                    continue

            if self.hkey in self.hkeys:
                Thread(target=self.history_append()).start()
                self.launch_hkey()
            elif self.hkey in self.rkeys:
                self.rkeys[self.hkey][0]()
            else:
                print("Invalid key...\nEnter 'h' for help\n")

    def launch_hkey(self):
        cmd, new_sh = self.hkeys[self.hkey][0], self.hkeys[self.hkey][2]
        if 'cmd_input' in self.__dict__:
            cmd += ' ' + self.cmd_input

        if new_sh == 'New Session':
            subprocess.Popen(cmd, shell=True, start_new_session=True)
        else:
            subprocess.run(cmd, shell=True)
        exit()

    def history_append(self):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if 'cmd_input' in self.__dict__:
            entry = f"{self.hkey}{self.cmd_input}".replace(',', '')
        else:
            entry = str(self.hkey).replace(',', '')

        with open(self.history_path, 'a') as hs:
            hs.write(f'{now},{entry}\n')

    def history_menu(self):
        import pandas as pd

        df = pd.read_csv(self.history_path)
        # Dataframe apenas com as hkeys (sem rkeys ou inputs)
        df = df[df.entry.isin(self.hkeys)]
        options = {'top': lambda num:
                   print(df['entry'].value_counts()[:int(num)]
                         / len(df.index) * 100),
                   'bot': lambda num:
                   print((df['entry'].value_counts()[-int(num):]
                          / len(df.index) * 100).iloc[::-1])}
        help_dialog = ' <top x>: top x\n <bot x>: bot x\n'

        print('History Menu')
        while True:
            entry = input('Search entry: ')
            if entry == 'q':
                print('Exited History Menu')
                return
            elif entry[:3] in options:
                options[entry[:3]](entry[4:])
            else:
                print(help_dialog)

    def show_hkeys(self):
        if len(self.hkeys) == 0:
            print("Hkeys list is empty...\nEnter 'ad' to add a new hkey\n")
            return

        [print(f"'{hkey}': {self.hkeys[hkey][1]}")
         for hkey in self.hkeys.keys()]
        print()

    def add_hkey(self):
        print('\nAdding mode')
        self.hkey = self.name_hkey()
        if self.hkey is False:
            return

        self.cmd = self.get_command()
        if self.cmd is False:
            return

        self.desc = self.get_description()
        if self.desc is False:
            return

        self.new_sh = self.get_shell_session()
        if self.new_sh is False:
            return

        if self.confirmation('Add') is False:
            return

        self.hkeys[self.hkey] = self.cmd, self.desc, self.new_sh
        self.update_hkeys()
        print('Added!\n')

    def remove_hkey(self):
        print('\nRemoving mode')
        self.hkey = self.hkey_search()
        if self.hkey is False:
            return

        self.cmd, self.desc, self.new_sh = self.hkeys[self.hkey]

        if self.confirmation('Remove') is False:
            return

        self.hkeys.pop(self.hkey)
        self.update_hkeys()
        print('Removed!\n')

    def edit_hkey(self):
        print('\nEditing mode')
        self.hkey = self.hkey_search()
        if self.hkey is False:
            return
        self.cmd, self.desc, self.new_sh = self.hkeys[self.hkey]
        section_opts = {'0': ['Hkey', self.hkey, self.name_hkey],
                        '1': ['Command', self.cmd, self.get_command],
                        '2': ['Description', self.desc, self.get_description],
                        '3': ['Shell', self.new_sh, self.get_shell_session]}

        while True:
            print()
            [print(f"[{opt}] {section_opts[opt][0]}: '{section_opts[opt][1]}'")
             for opt in section_opts.keys()]
            section = input("Edit what? (Enter 'q' to exit edition mode): ")
            if section == 'q':
                print('Exited edition mode\n')
                return
            elif section in section_opts:
                print(f'Current {section_opts[section][0]}: '
                      f"'{section_opts[section][1]}'")
                edition = section_opts[section][2]()

                if edition is False:
                    return
                elif edition == section_opts[section][1]:
                    print('Nothing has been changed...')
                    continue
                else:
                    print(f'{section_opts[section][0]} changed from '
                          f"'{section_opts[section][1]}' to '{edition}'")
                    section_opts[section][1] = edition
                    self.hkeys.pop(self.hkey)
                    self.hkeys[section_opts['0'][1]] = (section_opts['1'][1],
                                                        section_opts['2'][1],
                                                        section_opts['3'][1])

                    self.update_hkeys()
                    print('Edition Saved!')

    def hkey_search(self):
        while True:
            search_hkey = input('Enter hkey to search: ')
            if search_hkey == 'q':
                print('Aborted...\n')
                return False
            elif search_hkey in self.hkeys:
                return search_hkey
            elif search_hkey in self.rkeys:
                print(f"'{search_hkey}' is a reserved key")
            else:
                print(f"'{search_hkey}' not found")

    def name_hkey(self):
        print("\n[If you'll run the command with an input (e.g.: google "
              "<input>) make sure the hkey has a space at the end, "
              "otherwise don't leave a space]")

        while True:
            new_hkey = input("\nEnter the new hkey: ")
            if new_hkey == 'q':
                print('Aborted...\n')
                return False
            elif new_hkey in self.hkeys:
                print(f"'{new_hkey}' already exists for the following "
                      f"command: '{self.hkeys[new_hkey][0]}'")
            elif new_hkey in self.rkeys:
                print(f"'{new_hkey}' is a reserved key")
            else:
                return new_hkey

    def get_command(self):
        while True:
            cmd = input('Enter the full command to link to the hkey: ')
            if cmd == 'q':
                print('Aborted...\n')
                return False
            else:
                return cmd

    def get_description(self):
        while True:
            new_desc = input('Enter a description of the command: ')
            if new_desc == 'q':
                print('Aborted...\n')
                return False
            elif len(new_desc) > 80:
                print('Description is too long...')
            else:
                return new_desc

    def get_shell_session(self):
        new_sh = input(':: When launched, should the command be '
                       'started on a new shell session? [y/N] ')
        if new_sh.lower() in ('', 'n'):
            return 'Same Session'
        elif new_sh.lower() == 'y':
            return 'New Session'
        else:
            print('Aborted...\n')
            return False

    def confirmation(self, mode):
        ans = input(f'\nHkey: {self.hkey}\nCommand: {self.cmd}\n'
                    f'Description: {self.desc}\nShell: '
                    f'{self.new_sh}\n:: {mode} this entry? [Y/n] ')

        if ans.lower() in ('', 'y'):
            return True
        else:
            print('Aborted...\n')
            return False

    def update_hkeys(self):
        self.hkeys = dict(sorted(self.hkeys.items()))
        with open(self.hkeys_path, 'w') as hk:
            json.dump(self.hkeys, hk, indent=4)


Hkey().main()
