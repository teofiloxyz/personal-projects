#!/usr/bin/python3
"""Hkey (ou hotkey) atua como launcher (semelhante ao dmenu/rofi), através
da execução de comandos na shell. Este script podia ser substituido por
'bashrc aliases' no terminal, no entanto isso iria criar conflitos com comandos
da shell, dada a enorme diversidade de potenciais hotkeys.
Além das hkeys, existem as rkeys (ou reserved keys) que executam uma função
específica deste script. Em breve, o mesmo terá uma interface gráfica.
A versão princial está escrita em Go (Golang)"""

import subprocess
import json
import sys
from threading import Thread
from datetime import datetime


class Hkey:
    def __init__(self):
        self.hkeys_path = "hkeys_path"
        try:
            with open(self.hkeys_path, "r") as hk:
                self.hkeys = json.load(hk)
        except FileNotFoundError:
            self.hkeys = {}

        self.rkeys = {
            "ls": (self.show_hkeys, ": show hotkeys list"),
            "ad": (self.add_hkey, ": add entry to hotkeys list"),
            "rm": (self.remove_hkey, ": remove entry from hotkeys list"),
            "ed": (self.edit_hkey, ": edit entry from hotkeys list"),
            "hs": (self.history_menu, ": go to history menu"),
            "h": (lambda: print(self.help_dialog), ": show help dialog"),
            "q": (exit, ": quit"),
        }

        self.history_path = "history_path"
        self.help_dialog = "".join(
            [f"'{key}'{func[1]}\n" for key, func in self.rkeys.items()]
        )

    def main(self):
        while True:
            self.hkey = input("Enter hkey: ")
            if " " in self.hkey:
                self.hkey, self.cmd_input = self.hkey.split(" ", 1)
                self.hkey += " "
                if self.cmd_input.replace(" ", "") == "":
                    print("Input must be something...\n")
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
        if "cmd_input" in self.__dict__:
            cmd += " " + self.cmd_input

        if new_sh == "New Session":
            subprocess.Popen(cmd, shell=True, start_new_session=True)
        else:
            subprocess.run(cmd, shell=True)
        exit()

    def show_hkeys(self):
        if len(self.hkeys) == 0:
            print("Hkeys list is empty...\nEnter 'ad' to add a new hkey\n")
            return

        [
            print(f"'{hkey}': {self.hkeys[hkey][1]}")
            for hkey in self.hkeys.keys()
        ]
        print()


if len(sys.argv) == 2:
    option = sys.argv[1]
    if option == "history_menu":
        Hkey().history_menu()
    else:
        print("Argument error...")
else:
    Hkey().main()
