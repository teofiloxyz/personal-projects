#!/usr/bin/python3
"""Hkey (ou hotkey) atua como launcher, através da execução de comandos
na shell. Este script podia ser substituido por 'bashrc aliases' no
terminal, no entanto isso iria criar conflitos com comandos
da shell, dada a enorme diversidade de potenciais hotkeys.
Além das hkeys, existem as rkeys (ou reserved keys) que executam uma função
específica deste script. Em breve, o mesmo terá uma interface gráfica.
A versão princial está escrita em Go (Golang), esta versão
está incompleta"""

import subprocess
import json
from threading import Thread

from history import History
from json_editor import JsonEditor


class Hkey:
    def __init__(self) -> None:
        self.hkeys = self.load_hkeys()
        self.rkeys = {
            "ls": (self.show_hkeys, ": show hotkeys list"),
            "ad": (self.js.add_hkey, ": add entry to hotkeys list"),
            "rm": (self.js.remove_hkey, ": remove entry from hotkeys list"),
            "ed": (self.js.edit_hkey, ": edit entry from hotkeys list"),
            "hs": (self.hs.history_menu, ": go to history menu"),
            "h": (self.show_help_dialog, ": show help dialog"),
            "q": (exit, ": quit"),
        }
        self.hs = History()
        self.js = JsonEditor(self.hkeys, self.rkeys)

    def main(self) -> None:
        while True:
            hkey = input("Enter hkey: ")

            cmd_input = ""
            if " " in hkey:
                hkey, cmd_input = hkey.split(" ", 1)
                hkey += " "
                if cmd_input.replace(" ", "") == "":
                    print("Input must be something...\n")
                    continue

            if hkey in self.hkeys:
                Thread(target=self.hs.history_append(hkey, cmd_input)).start()
                self.launch_hkey(hkey, cmd_input)
            elif hkey in self.rkeys:
                self.rkeys[hkey][0]()
            else:
                print("Invalid key...\nEnter 'h' for help\n")

            self.hkeys = self.load_hkeys()

    def load_hkeys(self) -> dict[str, tuple]:
        hkeys_path = "hkeys_path"
        try:
            with open(hkeys_path, "r") as hk:
                return json.load(hk)
        except FileNotFoundError:
            return {}

    def launch_hkey(self, hkey: str, cmd_input: str = "") -> None:
        cmd, new_session = self.hkeys[hkey][0], self.hkeys[hkey][2]
        if cmd_input != "":
            cmd += " " + cmd_input

        if new_session == "New Session":
            subprocess.Popen(cmd, shell=True, start_new_session=True)
        else:
            subprocess.run(cmd, shell=True)
        exit()

    def show_help_dialog(self) -> None:
        print(
            "".join([f"'{key}'{func[1]}\n" for key, func in self.rkeys.items()])
        )

    def show_hkeys(self) -> None:
        if len(self.hkeys) == 0:
            print("Hkeys list is empty...\nEnter 'ad' to add a new hkey\n")
            return

        [
            print(f"'{hkey}': {self.hkeys[hkey][1]}")
            for hkey in self.hkeys.keys()
        ]
        print("")


if __name__ == "__main__":
    Hkey().main()
