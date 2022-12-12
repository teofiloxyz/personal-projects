#!/usr/bin/python3

from Tfuncs import rofi

import os
import subprocess

from utils import Utils


class Code:
    utils = Utils()
    options = {"python": ("python_path", ".py"), "bash": ("bash_path", ".sh")}

    def main(self, cmd_arg: str) -> None:
        code_info, entry = self.utils.divide_arg(cmd_arg, self.options)
        code_dir, extension = code_info

        files = self.get_files(code_dir, extension)
        results = dict()
        for file in files:
            file_results = self.search_entry_in_file(file, entry)
            if len(results) == 0:
                continue
            results[file] = file_results
        if len(results) == 0:
            rofi.message(f"Didn't find any line of code with '{entry}'")
            return

        dmenu_list = self.create_dmenu_list(results)
        choice = self.choose_with_rofi_dmenu(dmenu_list)
        if choice == "":
            return
        file, line = self.process_choice(choice, results)
        self.open_choice_in_vim(file, line)

    def get_files(self, dir_path: str, extension: str) -> list[str]:
        # put in utils
        cmd = (
            f"fd --hidden --extension {extension} --ignore-case "
            f"--full-path {dir_path}"
        )
        return (
            subprocess.run(cmd, shell=True, capture_output=True)
            .stdout.decode("utf-8")
            .split("\n")[:-1]
        )

    def get_file_lines(self, file: str) -> list[str]:
        with open(file, "r") as f:
            return f.readlines()

    def search_entry_in_file(self, file: str, entry: str) -> list[tuple]:
        results = list()
        lines = self.get_file_lines(file)
        for n, line in enumerate(lines, 1):
            if entry.lower() not in line.lower():
                continue
            line = " ".join(line.split())  # bc of indentation
            results.append((n, line))
        return results

    def create_dmenu_list(
        self, results: dict[str, list[tuple[str, str]]]
    ) -> list[str]:
        return [
            f"{result[1]} -> {os.path.basename(file)}: {result[0]}"
            for file, file_results in results.items()
            for result in file_results
        ]

    def choose_with_rofi_dmenu(self, dmenu: list) -> str:
        # put in utils
        prompt = "Choose which one to open in vim"
        return rofi.custom_dmenu(prompt, dmenu)

    def process_choice(self, choice: str, results: dict) -> tuple[str, str]:
        line, file = choice.split(" -> ")[-2], ""
        file_basename, line_num = choice.split(" -> ")[-1].split(": ")
        for result in results.values():
            if (
                result[0] == line
                and result[1].endswith(file_basename)
                and str(result[2]) == line_num
            ):
                file = result[1]
                break
        return file, line_num

    def open_choice_in_vim(self, file: str, line: str) -> None:
        cmd = f"alacritty -e nvim +{line} {file}"
        subprocess.run(cmd, shell=True)
