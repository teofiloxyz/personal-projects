# Search file or folder by title

from Tfuncs import rofi

import os
import subprocess


class Files:
    dir_path = "/home"

    def main(self, entry: str) -> None:
        results = self.search_entry(entry)
        if len(results) == 0:
            rofi.message(f"Didn't find in home any file with '{entry}'")
            return
        choice = self.choose_with_rofi_dmenu(results)
        if choice != "":
            self.open_choice_with_ranger(choice)

    def search_entry(self, entry: str) -> list[str]:
        cmd = f'fd --hidden --ignore-case "{entry}" {self.dir_path}'
        return (
            subprocess.run(cmd, shell=True, capture_output=True)
            .stdout.decode("utf-8")
            .split("\n")[:-1]
        )

    def choose_with_rofi_dmenu(self, results: list) -> str:
        prompt = "Choose which one to open with ranger"
        return rofi.custom_dmenu(prompt, results)

    def open_choice_with_ranger(self, choice: str) -> None:
        if not os.path.isdir(choice):
            choice = "--selectfile=" + choice

        cmd = f'alacritty -e ranger "{choice}"'
        subprocess.run(cmd, shell=True)
